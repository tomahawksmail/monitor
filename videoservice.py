from moviepy import ImageSequenceClip
from pathlib import Path
import platform


if platform.system() == "Windows":
    BASE_DIR = Path(r"C:\Users\admin.AD\PycharmProjects\test\screenshots")
    separator = "\\"
else:
    BASE_DIR = Path("/app/screenshots")
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    separator = "/"

for host_dir in BASE_DIR.iterdir():
    if host_dir.is_dir():
        for date_dir in host_dir.iterdir():
            if date_dir.is_dir():
                name = str(date_dir).split(separator)[-1]

                print(f"Found Directory: {date_dir}")
                print("_____________________________")
### Creating videofiles ###
                images = sorted(date_dir.glob("*.jpg"))

                if not images:
                    print(f"No images found in {date_dir}, skipping...")
                    continue  # Skip empty folders

                # Convert Path objects to strings
                image_files = [str(img) for img in images]
                print("Images:", image_files)

                # Create video clip, fps=1 means 1 frame per second
                clip = ImageSequenceClip(image_files, fps=1)

                # Output video file path
                video_path = date_dir / f"{name}.mp4"

                # Write video file
                clip.write_videofile(str(video_path), codec="libx264")

                print("✅ Video created at:", video_path)

### Delete all jpg files ####
                for file in image_files:
                    path = Path(file)
                    if path.exists():
                        path.unlink()
                        print("Deleted:", path)
                    else:
                        print("Not found:", path)
### Delete old video files ###



