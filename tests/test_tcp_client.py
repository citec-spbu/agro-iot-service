import socket
import struct

HOST = "127.0.0.1"
PORT = 9000

field_id = 1001  # серийник станции (int8)

# Пакет станции: AA 01 [8б field_id] [2б размер] [параметры...]
# param_id -> (name, byte_size): 0x00=wind_speed(2), 0x01=wind_direction(2), 0x02=rain(2)
payload = b""
payload += struct.pack(">Bh", 0x00, 35)    # wind_speed = 35
payload += struct.pack(">Bh", 0x01, 180)   # wind_direction = 180
payload += struct.pack(">Bh", 0x02, 50)    # rain = 50

packet = struct.pack(">BBQh", 0xAA, 0x01, field_id, len(payload)) + payload

print("Sending station packet:", packet.hex())

# Пакет датчика: AA 02 [8б field_id] [4б sensor_id] [2б размер] [параметры...]
# param_id -> (name, byte_size): 0x00=temperature(2), 0x01=soil_moisture(1)
sensor_payload = b""
sensor_payload += struct.pack(">Bh", 0x00, 225)   # temperature = 225
sensor_payload += struct.pack(">Bb", 0x01, 60)     # soil_moisture = 60 (1 byte)

sensor_packet = struct.pack(">BBQI", 0xAA, 0x02, field_id, 1) + struct.pack(">H", len(sensor_payload)) + sensor_payload

print("Sending sensor packet:", sensor_packet.hex())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(packet)           # станция
    s.sendall(sensor_packet)    # датчик
    print("Sent!")
