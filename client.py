##########################################
### Maksym Tsybulskyi 2025 uskoinc.com ###
##########################################
import time
import requests
import platform
import io
import os
from dotenv import load_dotenv
from datetime import datetime
import mss
from PIL import Image
from pynput import mouse, keyboard

# CENTRAL_ENV_PATH = r"\\dc-1\Install\GPO\monitor\.env"
CENTRAL_ENV_PATH = r"C:\Users\admin.AD\PycharmProjects\test\.env"

if os.path.exists(CENTRAL_ENV_PATH):
    load_dotenv(dotenv_path=CENTRAL_ENV_PATH)
    print(f"✅ Loaded centralized .env from {CENTRAL_ENV_PATH}")
else:
    print(f"⚠️ Central .env not found at {CENTRAL_ENV_PATH}")
    exit(0)

# Load settings
load_dotenv()
SERVER_URL = os.environ.get('API_URL')  # e.g. http://192.168.11.79:5566/upload
print("Using API:", SERVER_URL)

INTERVAL = int(os.environ.get('FREQUENCY', 5))
QUALITY = int(os.environ.get('QUALITY', 70))
VERSION = os.getenv("VERSION", "unknown")
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
                filename = f"{hostname}/{today_date}/{timestamp}.jpg"

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
