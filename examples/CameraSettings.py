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

html = """<!DOCTYPE html>
<html>
<head>
    <title>Micropython Camera Stream</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f0f0f0;
        }
        .container {
            display: flex;
            flex-direction: row;
            height: 100%;
            width: 100%;
        }
        .settings-container {
            display: flex;
            flex-direction: column;
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .setting {
            margin-bottom: 20px;
        }
        .video-container {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            padding: 20px;
        }
        img {
            width: 100%;
            height: auto;
        }
        .title-container {
            width: 100%;
            text-align: center;
            background-color: #ffffff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
    </style>
    <script>
        function updateValue(method, value) {
            console.log("Updating value: " + value + " using method: " + method);
            fetch('/set_' + method + '?value=' + value)
                .then(response => {
                    if (!response.ok) {
                        console.error("Error setting " + method);
                    } else {
                        console.log(method + " set to " + value);
                    }
                })
                .catch(error => {
                    console.error("Fetch error: ", error);
                });
        }

        function fetchValue(method, elementId) {
            console.log("Fetching value using method: " + method);
            fetch('/get_' + method)
                .then(response => response.text())
                .then(value => {
                    console.log(method + " value: " + value);
                    document.getElementById(elementId).value = value;
                })
                .catch(error => {
                    console.error("Fetch error: ", error);
                });
        }

        function updateCheckbox(method, elementId) {
            const checkbox = document.getElementById(elementId);
            const value = checkbox.checked ? 1 : 0;
            updateValue(method, value);
        }

        function fetchCheckbox(method, elementId) {
            console.log("Fetching value using method: " + method);
            fetch('/get_' + method)
                .then(response => response.text())
                .then(value => {
                    console.log(method + " value: " + value);
                    document.getElementById(elementId).checked = value === "1";
                })
                .catch(error => {
                    console.error("Fetch error: ", error);
                });
        }

        document.addEventListener("DOMContentLoaded", function() {
            fetchValue('quality', 'quality');
            fetchValue('wb_mode', 'wb_mode');
            fetchValue('contrast', 'contrast');
            fetchValue('brightness', 'brightness');
            fetchValue('saturation', 'saturation');
            fetchValue('sharpness', 'sharpness');
            fetchCheckbox('whitebal', 'whitebal');
            fetchCheckbox('gain_ctrl', 'gain_ctrl');
            fetchCheckbox('exposure_ctrl', 'exposure_ctrl');
            fetchCheckbox('hmirror', 'hmirror');
            fetchCheckbox('vflip', 'vflip');
            fetchCheckbox('aec2', 'aec2');
            fetchCheckbox('awb_gain', 'awb_gain');
        });
    </script>
</head>
<body>
    <div class="title-container">
        <h1>ESP32 Camera Stream</h1>
    </div>
    <div class="container">
        <div class="settings-container">
            <div class="setting">
                <label for="quality">JPEG quality:</label>
                <input type="range" id="quality" min="0" max="90" oninput="updateValue('quality', this.value)">
            </div>
            <div class="setting">
                <label for="wb_mode">White Balance Mode:</label>
                <select id="wb_mode" onchange="updateValue('wb_mode', this.value)">
                    <option value="0">Auto</option>
                    <option value="1">Sunny</option>
                    <option value="2">Cloudy</option>
                    <option value="3">Office</option>
                    <option value="4">Home</option>
                </select>
            </div>
            <div class="setting">
                <label for="contrast" title="The sensor contrast. Positive values increase contrast, negative values lower it. The total range is device-specific but is often from -2 to +2 inclusive.">Contrast:</label>
                <input type="range" id="contrast" min="-2" max="2" oninput="updateValue('contrast', this.value)">
            </div>
            <div class="setting">
                <label for="brightness" title="The sensor brightness. Positive values increase brightness, negative values lower it. The total range is device-specific but is often from -2 to +2 inclusive.">Brightness:</label>
                <input type="range" id="brightness" min="-2" max="2" oninput="updateValue('brightness', this.value)">
            </div>
            <div class="setting">
                <label for="saturation" title="The sensor saturation. Positive values increase saturation (more vibrant colors), negative values lower it (more muted colors). The total range is device-specific but the value is often from -2 to +2 inclusive.">Saturation:</label>
                <input type="range" id="saturation" min="-2" max="2" oninput="updateValue('saturation', this.value)">
            </div>
            <div class="setting">
                <label for="sharpness" title="The sensor sharpness. Positive values increase sharpness (more defined edges), negative values lower it (softer edges). The total range is device-specific but the value is often from -2 to +2 inclusive.">Sharpness:</label>
                <input type="range" id="sharpness" min="-2" max="2" oninput="updateValue('sharpness', this.value)">
            </div>
            <div class="setting">
                <label for="whitebal" title="When True, the camera attempts to automatically control white balance. When False, the wb_mode setting is used instead.">Auto White Balance:</label>
                <input type="checkbox" id="whitebal" onchange="updateCheckbox('whitebal', 'whitebal')">
            </div>
            <div class="setting">
                <label for="gain_ctrl" title="When True, the camera attempts to automatically control the sensor gain, up to the value in the gain_ceiling property. When False, the agc_gain setting is used instead.">Auto Gain Control:</label>
                <input type="checkbox" id="gain_ctrl" onchange="updateCheckbox('gain_ctrl', 'gain_ctrl')">
            </div>
            <div class="setting">
                <label for="exposure_ctrl" title="When True the camera attempts to automatically control the exposure. When False, the aec_value setting is used instead.">Auto Exposure Control:</label>
                <input type="checkbox" id="exposure_ctrl" onchange="updateCheckbox('exposure_ctrl', 'exposure_ctrl')">
            </div>
            <div class="setting">
                <label for="hmirror" title="When True the camera image is mirrored left-to-right.">Horizontal Mirror:</label>
                <input type="checkbox" id="hmirror" onchange="updateCheckbox('hmirror', 'hmirror')">
            </div>
            <div class="setting">
                <label for="vflip" title="When True the camera image is flipped top-to-bottom.">Vertical Flip:</label>
                <input type="checkbox" id="vflip" onchange="updateCheckbox('vflip', 'vflip')">
            </div>
            <div class="setting">
                <label for="aec2" title="When True the sensor’s “night mode” is enabled, extending the range of automatic gain control.">Night Mode:</label>
                <input type="checkbox" id="aec2" onchange="updateCheckbox('aec2', 'aec2')">
            </div>
            <div class="setting">
                <label for="awb_gain" title="Access the awb_gain property of the camera sensor.">AWB Gain:</label>
                <input type="checkbox" id="awb_gain" onchange="updateCheckbox('awb_gain', 'awb_gain')">
            </div>
        </div>
        <div class="video-container">
            <img src="/stream">
        </div>
    </div>
</body>
</html>
"""

async def stream_camera(writer):
    try:
        cam.init()

        writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n')
        await writer.drain()

        while True:
            frame = cam.capture()
            if frame:
                writer.write(b'--frame\r\n')
                writer.write(b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
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

