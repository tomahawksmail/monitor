##########################################
### Maksym Tsybulskyi 2025 uskoinc.com ###
##########################################
import time
import requests
import platform
import io
import os
from datetime import datetime
import configparser
import mss
from PIL import Image
from pynput import mouse, keyboard

CONFIG_FILE = "options.ini"

# Load the INI file
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# Read values
SERVER_URL = config["DEFAULT"].get("API_URL")
TTLVIDEO = config["DEFAULT"].getint("TTLVIDEO", fallback=3)
VERSION = config["DEFAULT"].get("VERSION", fallback="unknown")
INTERVAL = config["DEFAULT"].getint("FREQUENCY", fallback=5)
QUALITY = config["DEFAULT"].getint("QUALITY", fallback=50)

user = os.getlogin()
hostname = platform.node() or "unknown_host"

# Activity flag
user_active = False

# Mouse & keyboard listeners
def on_mouse_move(x, y):
    global user_active
    user_active = True

def on_mouse_click(x, y, button, pressed):
    global user_active
    user_active = True

def on_key_press(key):
    global user_active
    user_active = True


mouse_listener = mouse.Listener(on_move=on_mouse_move, on_click=on_mouse_click)
keyboard_listener = keyboard.Listener(on_press=on_key_press)
mouse_listener.start()
keyboard_listener.start()


print(f"[INFO] Client started for host: {hostname}")

try:
    while True:
        if user_active:
            timestamp = datetime.now().strftime("%H-%M-%S")
            today_date = datetime.now().strftime("%Y-%m-%d")

            with mss.mss() as sct:
                screenshot = sct.grab(sct.monitors[0])
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG", quality=QUALITY)
                img_bytes.seek(0)

                # IMPORTANT — no slashes inside filename
                filename = f"{hostname}/{today_date}/{user}/{timestamp}.jpg"

                files = {'file': (filename, img_bytes, 'image/jpeg')}

                # send folder info separately
                data = {
                    "hostname": hostname,
                    "date": today_date
                }

                try:
                    r = requests.post(SERVER_URL, files=files, data=data, timeout=10)
                    print(f"[{timestamp}] Uploaded OK ({r.status_code})")
                except Exception as e:
                    print(f"[{timestamp}] Upload ERROR: {e}")

            # reset flag
            user_active = False

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("Client stopped.")
