import network
import asyncio
import time
from camera import Camera, FrameSize, PixelFormat

cam = Camera(frame_size=FrameSize.VGA, pixel_format=PixelFormat.JPEG, jpeg_quality=85, init=False)
# WLAN config
ssid = 'Zopilote'
password = '2018@Ihringen'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    time.sleep(1)

print(f'Connected! IP: {station.ifconfig()[0]}. Open this IP in your browser')

with open("ESP32cam.html", 'r') as file:
    html = file.read()

async def stream_camera(writer):
    try:
        cam.init()

        writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n')
        await writer.drain()

        while True:
            frame = cam.capture()
            if frame:
                writer.write(b'--frame\r\nContent-Type: image/jpeg\r\n\r\n')
                await writer.drain()
                writer.write(frame)
                await writer.drain()
                writer.write(b'\r\n')
                await writer.drain()
            else:
                pass
    finally:
        cam.deinit()
        writer.close()
        await writer.wait_closed()
        print("Streaming stopped and camera deinitialized.")

async def handle_client(reader, writer):
    try:
        request = await reader.read(1024)
        request = request.decode()

        if 'GET /stream' in request:
            print("Start streaming...")
            await stream_camera(writer)

        elif 'GET /set_' in request:
            method_name = request.split('GET /set_')[1].split('?')[0]
            value = int(request.split('value=')[1].split(' ')[0])
            set_method = getattr(cam, f'set_{method_name}', None)
            if callable(set_method):
                print(f"setting {method_name} to {value}")
                set_method(value)
                response = 'HTTP/1.1 200 OK\r\n\r\n'
                writer.write(response.encode())
                await writer.drain()
            else:
                response = 'HTTP/1.1 404 Not Found\r\n\r\n'
                writer.write(response.encode())
                await writer.drain()

        elif 'GET /get_' in request:
            method_name = request.split('GET /get_')[1].split(' ')[0]
            get_method = getattr(cam, f'get_{method_name}', None)
            if callable(get_method):
                value = get_method()
                print(f"{method_name} is {value}")
                response = f'HTTP/1.1 200 OK\r\n\r\n{value}'
                writer.write(response.encode())
                await writer.drain()
            else:
                response = 'HTTP/1.1 404 Not Found\r\n\r\n'
                writer.write(response.encode())
                await writer.drain()

        else:
            writer.write('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'.encode() + html.encode())
            await writer.drain()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

# Funktion zum Starten des Servers
async def start_server():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print(f'Server is running on {station.ifconfig()[0]}:80')
    while True:
        await asyncio.sleep(3600)  # Server läuft kontinuierlich; wir blockieren die Schleife

# Starte den asyncio-Loop
try:
    asyncio.run(start_server())
except KeyboardInterrupt:
    print("Server stopped")
