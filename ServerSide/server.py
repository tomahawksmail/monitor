from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session, send_file
from pathlib import Path
import shutil
import platform
from datetime import datetime
from ldap_utils import ldap_auth, is_user_in_group, KEY


app = Flask(__name__)
app.secret_key = KEY


host = platform.uname()[1]


if platform.system() == "Windows":
    BASE_DIR = Path(r"/screenshots")
else:
    BASE_DIR = Path("/app/screenshots")
    BASE_DIR.mkdir(parents=True, exist_ok=True)

@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    return redirect("index")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # LDAP auth
        if not ldap_auth(username, password):
            flash("Invalid username/password")
            return redirect(url_for("login"))

        # Group check
        if not is_user_in_group(username):
            flash("You are not allowed to access this system.")
            return redirect(url_for("login"))

        session["username"] = username
        return redirect(url_for("index"))
    else:
        return render_template('login.html')


@app.route("/download/<host>/<date>/<user>/<filename>")
def download_file(host, date, user, filename):
    file_path = BASE_DIR / host / date / user / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return "File not found", 404


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/data")
def data():
    """Return disk usage info in JSON for the gauge."""
    return jsonify(get_space())


def safe_date_parse(name):
    """Try to parse folder name as date. Fallback: lexical sort."""
    try:
        return datetime.strptime(name, "%Y-%m-%d")
    except:
        return name  # fallback for non-date folder names


@app.route("/index", methods=["GET", "POST"])
def index():
    info = get_space()

    data = {}
    total_screens = 0
    total_videos = 0

    # Sort host directories by name (or modify if needed)
    host_dirs = sorted(
        [d for d in BASE_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.name
    )

    for host_dir in host_dirs:
        host_data = {}

        # Sort dates inside host
        date_dirs = sorted(
            [d for d in host_dir.iterdir() if d.is_dir()],
            key=lambda d: safe_date_parse(d.name),
            reverse=True  # newest first
        )

        for date_dir in date_dirs:
            date_data = {}

            # Sort users inside date
            user_dirs = sorted(
                [d for d in date_dir.iterdir() if d.is_dir()],
                key=lambda d: d.name
            )

            for user_dir in user_dirs:
                screens = list(user_dir.glob("*.jpg"))
                videos = list(user_dir.glob("*.mp4"))

                screen_size = get_folder_size(screens)
                video_size = get_folder_size(videos)

                total_screens += screen_size
                total_videos += video_size

                date_data[user_dir.name] = {
                    "screens": {
                        "files": sorted([f.name for f in screens]),
                        "count": len(screens),
                        "size": f"{screen_size:.2f} MB"
                    },
                    "videos": {
                        "files": sorted([f.name for f in videos]),
                        "count": len(videos),
                        "size": f"{video_size:.2f} MB"
                    }
                }

            host_data[date_dir.name] = date_data

        data[host_dir.name] = host_data

    return render_template(
        "index.html",
        data=data,
        sum=round(total_screens, 2),
        vsum=round(total_videos, 2),
        info=info,
        host=host
    )


@app.route("/upload", methods=["POST"])
def upload():
    return upload_screenshot()

def upload_screenshot():

    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    original_name = uploaded_file.filename
    print("Received filename:", original_name)

    parts = original_name.split("/")

    if len(parts) == 4:
        hostname, today_date, username, filename = parts
    elif len(parts) == 3:
        # older client format: hostname/date/filename
        hostname, today_date, filename = parts
        username = "unknown"
    else:
        # fallback
        hostname = "unknown_host"
        today_date = ""
        username = "unknown"
        filename = original_name

    # Build path: BASE_DIR/hostname/date/username/
    file_path = BASE_DIR / hostname / today_date / username
    file_path.mkdir(parents=True, exist_ok=True)

    file_path = file_path / filename

    uploaded_file.save(file_path)

    print(f"Saved screenshot: {file_path}")

    return jsonify({"status": "ok"}), 200

def get_space():
    total, used, free = shutil.disk_usage("/mnt/nfs/nfs-server")
    print(f"Total: {total}, Used: {used}, Free: {free}")
    percent = round(used / total * 100, 1)
    return {
        "total": round(total / (1024 ** 3), 2),
        "used": round(used / (1024 ** 3), 2),
        "free": round(free / (1024 ** 3), 2),
        "percent": percent
    }
def get_folder_size(files):
    """Return total size (MB) of all given files."""
    return sum(f.stat().st_size for f in files) / (1024 * 1024)

# if __name__ == "__main__":
#     app.run(host="192.168.11.79", port=5566)
