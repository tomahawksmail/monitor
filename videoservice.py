import cv2
import os
from pathlib import Path

# Folder containing JPEG screenshots
input_folder = Path("screenshots/PC-01")  # replace with your host folder
output_file = Path("output_video.mp4")

# Video settings
fps = 10  # frames per second
frame_size = None  # will be determined from first image

# Get sorted list of JPEG files
image_files = sorted([f for f in input_folder.glob("*.jpg")])

if not image_files:
    print("No images found in folder.")
    exit()

# Read first image to get frame size
first_image = cv2.imread(str(image_files[0]))
height, width, channels = first_image.shape
frame_size = (width, height)

# Initialize VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 'XVID' or 'mp4v'
video_writer = cv2.VideoWriter(str(output_file), fourcc, fps, frame_size)

# Add each image to the video
for img_file in image_files:
    img = cv2.imread(str(img_file))
    if img.shape[1] != width or img.shape[0] != height:
        # Resize if necessary
        img = cv2.resize(img, frame_size)
    video_writer.write(img)

video_writer.release()
print(f"Video created: {output_file}")


# # Background cleanup thread
# def cleanup_old_screenshots():
#     while True:
#         now = datetime.now()
#         for host_dir in BASE_DIR.iterdir():
#             if host_dir.is_dir():
#                 for file in host_dir.iterdir():
#                     if file.is_file():
#                         mtime = datetime.fromtimestamp(file.stat().st_mtime)
#                         if now - mtime > timedelta(minutes=RETENTION_MINUTES):
#                             try:
#                                 file.unlink()
#                                 print(f"Deleted old screenshot: {file}")
#                             except Exception as e:
#                                 print(f"Error deleting file {file}: {e}")
#         time.sleep(60)  # check every 1 minute
#
# # Start cleanup thread
# threading.Thread(target=cleanup_old_screenshots, daemon=True).start()