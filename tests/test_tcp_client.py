import socket

HOST = "127.0.0.1"
PORT = 9006

# hardware_id=7
# temperature=-9.9, humidity=65, wind_speed=7.0, wind_direction=180, rain=10.0
station_hex = (
    "aa"                  # header
    "01"                  # packet_type: station
    "0000000000000007"    # hardware_id
    "000e"                # payload length: 14 bytes
    "00" "0321"           # temperature: (801 - 900) / 10 = -9.9
    "01" "41"             # humidity: 65
    "02" "0124"           # wind_speed: 35 / 5 = 7.0
    "03" "01b5"           # wind_direction: 180
    "04" "0133"           # rain: 50 / 5 = 10.0
)

# hardware_id=7, sensor_id=42
# humiditya=55, temperaturea=20.2, soil_moisturez=65, temperaturez=35.4
sensor_hex = (
    "aa"                  # header
    "02"                  # packet_type: sensor
    "0000000000000007"    # hardware_id
    "0000002a"            # sensor_id: 42
    "0008"                # payload length: 8 bytes
    "00" "37"             # humiditya: 55
    "01" "80"             # temperaturea: -20 + 128 * 80 / 255 = 20.2
    "02" "41"             # soil_moisturez: 65
    "03" "80"             # temperaturez: -55 + 128 * 180 / 255 = 35.4
)

station_packet = bytes.fromhex(station_hex)
sensor_packet = bytes.fromhex(sensor_hex)

print(f"-> {HOST}:{PORT}")
print(f"station: {station_packet.hex()}")
print(f"sensor:  {sensor_packet.hex()}")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.sendall(station_packet)
sock.sendall(sensor_packet)
sock.close()

print("sent OK")
