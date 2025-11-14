import cv2
import os
import platform
from pathlib import Path
from datetime import datetime

# ==== CONFIGURATION ====
if platform.system() == "Windows":
    BASE_DIR = Path(r"C:\Users\admin.AD\PycharmProjects\test\screenshots")
else:
    BASE_DIR = Path("/app/screenshots")
VIDEO_FPS = 10
VIDEO_CODEC = 'mp4v'

def create_videos_for_all_dirs():
    # Loop through all subdirectories (PC + date folders)
    for subdir in BASE_DIR.iterdir():
        if subdir.is_dir():
            images = sorted(subdir.glob("*.png"))
            if not images:
                continue  # skip empty directories

            # Get first image to determine size
            first_image = cv2.imread(str(images[0]))
            height, width, _ = first_image.shape

            # Create video filename: include PC name and date from folder
            video_filename = BASE_DIR / f"{subdir.name}.mp4"

            fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC)
            video_writer = cv2.VideoWriter(str(video_filename), fourcc, VIDEO_FPS, (width, height))

            for img_path in images:
                img = cv2.imread(str(img_path))
                video_writer.write(img)

            video_writer.release()
            print(f"Video created: {video_filename}")

            # Delete original screenshots
            for img_path in images:
                img_path.unlink()
            print(f"Deleted {len(images)} screenshots from {subdir.name}")

if __name__ == "__main__":
    create_videos_for_all_dirs()
