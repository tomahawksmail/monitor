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


CENTRAL_ENV_PATH = r"\\dc-1\Install\GPO\monitor\.env"

if os.path.exists(CENTRAL_ENV_PATH):
    load_dotenv(dotenv_path=CENTRAL_ENV_PATH)
    print(f"✅ Loaded centralized .env from {CENTRAL_ENV_PATH}")
else:
    print(f"⚠️ Central .env not found at {CENTRAL_ENV_PATH}")
    exit(0)

# Load settings
load_dotenv()
SERVER_URL = os.environ.get('API_URL')
INTERVAL = int(os.environ.get('FREQUENCY', 5))
QUALITY = int(os.environ.get('QUALITY', 70))
VERSION = os.getenv("VERSION", "unknown")
hostname = platform.node() or "unknown_host"


# Flag to track user activity
user_active = False

# Mouse and keyboard listeners
def on_mouse_move(x, y):
    # print("Mouse moved")
    global user_active
    user_active = True

def on_mouse_click(x, y, button, pressed):
    global user_active
    user_active = True

def on_key_press(key):
    # print("key pressed")
    global user_active
    user_active = True


def on_key_combination():
    print("Key combination 'ctrl+shift+a' pressed!")


mouse_listener = mouse.Listener(on_move=on_mouse_move, on_click=on_mouse_click)
keyboard_listener = keyboard.Listener(on_press=on_key_press)
mouse_listener.start()



print(f"[INFO] Client started for host: {hostname}")

try:
    while True:
        if user_active:
            timestamp = datetime.now().strftime("%H-%M-%S")
            today_date = datetime.now().strftime("%Y-%m-%d")
            with mss.mss() as sct:
                # Capture all monitors
                screenshot = sct.grab(sct.monitors[0])
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG", quality=QUALITY)
                img_bytes.seek(0)

                filename = f"{hostname}/{today_date}/{timestamp}.jpg"
                files = {'file': (filename, img_bytes, 'image/jpeg')}

                try:
                    r = requests.post(SERVER_URL, files=files, timeout=10)
                    print(f"[{timestamp}] Uploaded {filename}: {r.status_code}")
                except Exception as e:
                    print(f"[{timestamp}] Error uploading {filename}: {e}")

            # Reset activity flag
            user_active = False

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("Client stopped.")



