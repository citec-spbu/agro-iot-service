"""Минимальный TCP-клиент для отладки парсера агро-IoT-сервиса.

Шлёт по одному station- и sensor-пакету на TCP-сервер (`localhost:9000` по умолчанию).
Перед запуском станция с `HARDWARE_ID` должна быть зарегистрирована через
`POST /api/iot/stations` — иначе сервис отбросит пакеты (FK).

Запуск:
    HARDWARE_ID=12345 python tests/test_tcp_client.py
"""
import os
import socket
import struct
import sys

HOST = os.environ.get("IOT_TCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("IOT_TCP_PORT", "9000"))
HARDWARE_ID = int(os.environ.get("HARDWARE_ID", "12345"))
SENSOR_ID = int(os.environ.get("SENSOR_ID", "1"))


def build_station_packet(hw_id: int) -> bytes:
    # STATION_PARAMS: 0x02 wind_speed (2B), 0x03 wind_direction (2B), 0x04 rain (2B)
    payload = (
        struct.pack(">Bh", 0x02, 35)
        + struct.pack(">Bh", 0x03, 180)
        + struct.pack(">Bh", 0x04, 50)
    )
    return struct.pack(">BBQH", 0xAA, 0x01, hw_id, len(payload)) + payload


def build_sensor_packet(hw_id: int, sensor_id: int) -> bytes:
    # SENSOR_PARAMS: 0x00 temperature (2B), 0x01 soil_moisture (1B)
    payload = struct.pack(">Bh", 0x00, 220) + struct.pack(">Bb", 0x01, 65)
    return (
        struct.pack(">BBQIH", 0xAA, 0x02, hw_id, sensor_id, len(payload))
        + payload
    )


def main() -> None:
    pkt_station = build_station_packet(HARDWARE_ID)
    pkt_sensor = build_sensor_packet(HARDWARE_ID, SENSOR_ID)

    print(f"-> {HOST}:{PORT} | hardware_id={HARDWARE_ID} sensor_id={SENSOR_ID}")
    print(f"   station ({len(pkt_station)}b): {pkt_station.hex()}")
    print(f"   sensor  ({len(pkt_sensor)}b):  {pkt_sensor.hex()}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall(pkt_station)
        sock.sendall(pkt_sensor)
    print("sent OK")


if __name__ == "__main__":
    try:
        main()
    except (ConnectionRefusedError, socket.timeout) as exc:
        print(f"connect failed: {exc}", file=sys.stderr)
        sys.exit(1)
