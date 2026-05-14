"""
Минимальный TCP-клиент для отладки парсера агро-IoT-сервиса.
"""
import os
import socket
import struct
import sys

HOST = os.environ.get("IOT_TCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("IOT_TCP_PORT", "9000"))
HARDWARE_ID = int(os.environ.get("HARDWARE_ID", "12345"))
SENSOR_ID = int(os.environ.get("SENSOR_ID", "1"))


def encode_station_temperature(value: float) -> bytes:
    return struct.pack(">h", round(value * 10 + 900))


def encode_station_offset_pair(value: float, *, scale: int = 1) -> bytes:
    raw = round(value * scale)
    return bytes([(raw >> 8) + 1, (raw & 0xFF) + 1])


def encode_air_temperature(value: float) -> int:
    return round((value + 20) * 255 / 80)


def encode_soil_temperature(value: float) -> int:
    return round((value + 55) * 255 / 180)


def build_station_packet(hw_id: int) -> bytes:
    payload = (
        bytes([0x00]) + encode_station_temperature(-9.9)
        + bytes([0x01, 65])
        + bytes([0x02]) + encode_station_offset_pair(7.0, scale=5)
        + bytes([0x03]) + encode_station_offset_pair(180)
        + bytes([0x04]) + encode_station_offset_pair(10.0, scale=5)
    )
    return struct.pack(">BBQH", 0xAA, 0x01, hw_id, len(payload)) + payload


def build_sensor_packet(hw_id: int, sensor_id: int) -> bytes:
    payload = bytes(
        [
            0x00, 55,
            0x01, encode_air_temperature(20.0),
            0x02, 65,
            0x03, encode_soil_temperature(35.0),
        ]
    )
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
