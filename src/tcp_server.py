import asyncio
import logging
import struct
from datetime import datetime

from src.config import settings
from src.repositories.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from src.schemas.iot_data import SensorDataCreateSchema, StationDataCreateSchema

logger = logging.getLogger(__name__)

HEADER_BYTE = 0xAA
PACKET_STATION = 0x01
PACKET_SENSOR = 0x02

# param_id -> (name, byte_size)
STATION_PARAMS = {
    0x00: ("temperature", 2),
    0x01: ("soil_moisture", 1),
    0x02: ("wind_speed", 2),
    0x03: ("wind_direction", 2),
    0x04: ("rain", 2),
}

SENSOR_PARAMS = {
    0x00: ("temperaturea", 1),
    0x01: ("soil_moisturea", 1),
    0x02: ("temperaturez", 1),
    0x03: ("soil_moisturez", 1),
}


def _decode_offset_pair(value: bytes) -> int:
    high, low = value
    return ((high - 1) << 8) + low - 1


def _normalize_station_params(params: dict[str, int | bytes]) -> dict[str, int | float]:
    normalized = {}
    for name, value in params.items():
        if name == "temperature":
            raw_temperature = int.from_bytes(value, byteorder="big", signed=True)
            normalized[name] = round((raw_temperature - 900) / 10, 1)
        elif name == "wind_speed":
            normalized[name] = round(_decode_offset_pair(value) / 5, 1)
        elif name == "wind_direction":
            normalized[name] = _decode_offset_pair(value)
        elif name == "rain":
            normalized[name] = round(_decode_offset_pair(value) / 5, 1)
        else:
            normalized[name] = value
    return normalized


async def _save_station_data(hardware_id: int, params: dict) -> None:
    now_local = datetime.now(settings.TZ).replace(tzinfo=None)
    uow = SQLAlchemyUnitOfWork()
    try:
        async with uow:
            station = await uow.stations.read(hardware_id=hardware_id)
            if station is None:
                logger.warning(
                    "Unknown hardware_id=%s, station packet dropped", hardware_id
                )
                return
            schema = StationDataCreateSchema(
                field_id=station.field_id,
                payload=params,
                date_time=now_local,
            )
            await uow.station_data.create(schema.model_dump())
            await uow.stations.update_last_seen(hardware_id, now_local)
            await uow.commit()
    except Exception:
        logger.exception("Failed to persist station data | hardware=%s", hardware_id)


async def _save_sensor_data(hardware_id: int, sensor_id: int, params: dict) -> None:
    now_local = datetime.now(settings.TZ).replace(tzinfo=None)
    uow = SQLAlchemyUnitOfWork()
    try:
        async with uow:
            station = await uow.stations.read(hardware_id=hardware_id)
            if station is None:
                logger.warning(
                    "Unknown hardware_id=%s, sensor packet dropped", hardware_id
                )
                return
            schema = SensorDataCreateSchema(
                field_id=station.field_id,
                sensor_id=sensor_id,
                payload=params,
                date_time=now_local,
            )
            await uow.sensor_data.create(schema.model_dump())
            await uow.stations.update_last_seen(hardware_id, now_local)
            await uow.commit()
    except Exception:
        logger.exception(
            "Failed to persist sensor data | hardware=%s | sensor=%s",
            hardware_id, sensor_id,
        )


class SensorProtocol(asyncio.Protocol):
    def __init__(self):
        self._buffer = b""

    def connection_made(self, transport):
        peer = transport.get_extra_info("peername")
        logger.debug("Device connected: %s", peer)
        self._transport = transport

    def data_received(self, data: bytes):
        self._buffer += data
        self._process_buffer()

    def connection_lost(self, exc):
        logger.debug("Device disconnected")

    def _process_buffer(self):
        while len(self._buffer) >= 2:
            if self._buffer[0] != HEADER_BYTE:
                self._buffer = self._buffer[1:]
                continue

            packet_type = self._buffer[1]

            if packet_type == PACKET_STATION:
                if not self._parse_station():
                    return
            elif packet_type == PACKET_SENSOR:
                if not self._parse_sensor():
                    return
            else:
                self._buffer = self._buffer[1:]

    def _parse_station(self) -> bool:
        # [AA][01][8б hardware_id][2б размер][payload...]
        header_size = 12
        if len(self._buffer) < header_size:
            return False

        hardware_id = struct.unpack(">Q", self._buffer[2:10])[0]
        data_size = struct.unpack(">H", self._buffer[10:12])[0]

        total = header_size + data_size
        if len(self._buffer) < total:
            return False

        payload = self._buffer[12:total]
        self._buffer = self._buffer[total:]

        raw_params = self._parse_params(STATION_PARAMS, payload, raw_two_byte=True)
        params = _normalize_station_params(raw_params)
        logger.debug("Station packet | hardware=%s | %s", hardware_id, params)
        asyncio.create_task(_save_station_data(hardware_id, params))
        return True

    def _parse_sensor(self) -> bool:
        # [AA][02][8б hardware_id][4б sensor_id][2б размер][payload...]
        header_size = 16
        if len(self._buffer) < header_size:
            return False

        hardware_id = struct.unpack(">Q", self._buffer[2:10])[0]
        sensor_id = struct.unpack(">I", self._buffer[10:14])[0]
        data_size = struct.unpack(">H", self._buffer[14:16])[0]

        total = header_size + data_size
        if len(self._buffer) < total:
            return False

        payload = self._buffer[16:total]
        self._buffer = self._buffer[total:]

        params = self._parse_params(SENSOR_PARAMS, payload)
        logger.debug(
            "Sensor packet | hardware=%s | sensor=%d | %s",
            hardware_id, sensor_id, params,
        )
        asyncio.create_task(_save_sensor_data(hardware_id, sensor_id, params))
        return True

    def _parse_params(
        self, mapping: dict, payload: bytes, *, raw_two_byte: bool = False
    ) -> dict[str, int | bytes]:
        params = {}
        offset = 0
        while offset < len(payload):
            if offset + 1 > len(payload):
                break

            param_id = payload[offset]
            offset += 1

            if param_id not in mapping:
                logger.warning("Unknown param_id: 0x%02X", param_id)
                break

            name, size = mapping[param_id]

            if offset + size > len(payload):
                logger.warning("Truncated payload for param %s", name)
                break

            chunk = payload[offset:offset + size]
            if size == 1:
                value = chunk[0]
            elif raw_two_byte:
                value = chunk
            else:
                value = struct.unpack(">h", chunk)[0]

            params[name] = value
            offset += size

        return params


async def start_tcp_server(host: str, port: int):
    loop = asyncio.get_event_loop()
    server = await loop.create_server(
        lambda: SensorProtocol(),
        host, port,
    )
    logger.info("TCP sensor server listening on %s:%d", host, port)
    return server
