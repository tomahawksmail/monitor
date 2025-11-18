from moviepy import ImageSequenceClip
from pathlib import Path
import platform
import time

# Detect base path
if platform.system() == "Windows":
    BASE_DIR = Path(r"/screenshots")
else:
    BASE_DIR = Path("/app/screenshots")
    BASE_DIR.mkdir(parents=True, exist_ok=True)

TTL_SECONDS = 5 * 24 * 60 * 60   # days → seconds

# -------------------------------------------------------------
#            CREATE VIDEO FOR ONE USER DIRECTORY
# -------------------------------------------------------------
def create_video_for_user(user_dir: Path):
    """
    Convert all JPG files inside a user directory into a video.
    Example path: host/date/user/
    """
    user = user_dir.name
    date = user_dir.parent.name
    host = user_dir.parent.parent.name

    images = sorted(user_dir.glob("*.jpg"))
    if not images:
        print(f"[SKIP] No JPGs in {user_dir}")
        return

    image_files = [str(img) for img in images]
    print(f"[INFO] Creating video for {host}/{date}/{user} from {len(images)} images")

    video_name = f"{date}-{user}.mp4"
    video_path = user_dir / video_name

    try:
        clip = ImageSequenceClip(image_files, fps=1)
        clip.write_videofile(str(video_path), codec="libx264")
        print(f"✅ Video created: {video_path}")

    except Exception as e:
        print("❌ Error creating video:", e)
        return

    delete_images(images)


# -------------------------------------------------------------
#            DELETE ALL JPG FILES FOR A USER
# -------------------------------------------------------------
def delete_images(images):
    for file in images:
        try:
            file.unlink()
            print("🗑️ Deleted:", file)
        except Exception as e:
            print("❌ Error deleting:", file, e)


# -------------------------------------------------------------
#        DELETE OLD VIDEOS (older than TTL days)
# -------------------------------------------------------------
def delete_old_videos():
    now = time.time()


    for mp4 in BASE_DIR.rglob("*.mp4"):
        age = now - mp4.stat().st_mtime

        if age > TTL_SECONDS:
            try:
                mp4.unlink()
                print(f"🗑️ Deleted old video: {mp4}")
            except Exception as e:
                print(f"❌ Could not delete {mp4}", e)


# -------------------------------------------------------------
#                   PROCESS ENTIRE TREE
# -------------------------------------------------------------
def process_all_hosts():
    print("\n====== START PROCESSING ======\n")

    for host_dir in BASE_DIR.iterdir():
        if not host_dir.is_dir():
            continue

        print(f"\n📁 HOST: {host_dir.name}")

        for date_dir in host_dir.iterdir():
            if not date_dir.is_dir():
                continue

            print(f"  📅 DATE: {date_dir.name}")

            for user_dir in date_dir.iterdir():
                if not user_dir.is_dir():
                    continue
                print(f"    👤 USER: {user_dir.name}")
                create_video_for_user(user_dir)
    delete_old_videos()
    print("\n====== DONE ======\n")


# -------------------------------------------------------------
if __name__ == "__main__":
    process_all_hosts()
