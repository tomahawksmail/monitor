from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
import secrets
from pathlib import Path
import os
from dotenv import load_dotenv
import shutil
import platform
load_dotenv()
from ldap_utils import ldap_auth, is_user_in_group

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(16))


host = platform.uname()[1]


if platform.system() == "Windows":
    BASE_DIR = Path(r"C:\Users\admin.AD\PycharmProjects\test\screenshots")
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




@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/data")
def data():
    """Return disk usage info in JSON for the gauge."""
    return jsonify(get_space())


@app.route("/index", methods=["GET", "POST"])
def index():
    info = get_space()
    if request.method == "GET":
        data = {}
        sum = 0
        vsum = 0

        for host_dir in BASE_DIR.iterdir():
            if host_dir.is_dir():
                host_info = {}
                total_host_size = 0.0
                total_video_size = 0.0

                for date_dir in host_dir.iterdir():
                    if date_dir.is_dir():

                        # Collect screenshot files
                        files = list(date_dir.glob("*.jpg"))

                        # Collect video files
                        videofiles = list(date_dir.glob("*.mp4"))

                        # Calculate folder sizes
                        size_mb = get_folder_size(files)
                        vsize_mb = get_folder_size(videofiles)

                        sum += size_mb
                        vsum += vsize_mb

                        total_host_size += size_mb
                        total_video_size += vsize_mb

                        host_info[date_dir.name] = {
                            "screens": {
                                "files": [f.name for f in files],
                                "size": f"{size_mb:.2f} MB",
                                "count": len(files),
                            },
                            "videos": {
                                "files": [f.name for f in videofiles],
                                "size": f"{vsize_mb:.2f} MB",
                                "count": len(videofiles),
                            }
                        }

                data[host_dir.name] = {
                    "dates": host_info,
                    "total_screenshots_size": f"{total_host_size:.2f} MB",
                    "total_video_size": f"{total_video_size:.2f} MB",
                }

        return render_template(
            "index.html",
            data=data,
            sum=round(sum, 2),
            vsum=round(vsum, 2),
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

    # Expect filename format: hostname/YYYY-MM-DD/HHMMSS.jpg
    original_name = uploaded_file.filename
    print("Received filename:", original_name)

    if "/" in original_name:
        hostname, today_date, filename = original_name.split("/", 2)
    else:
        hostname = "unknown_host"
        filename = original_name
        today_date = ""

    # Build full path
    file_path = BASE_DIR / hostname
    if today_date:
        file_path = file_path / today_date
    file_path.mkdir(parents=True, exist_ok=True)  # make sure folders exist

    file_path = file_path / filename

    # Save file
    uploaded_file.save(file_path)
    print(f"Saved screenshot from {hostname}: {file_path}")

    return jsonify({"status": "ok"}), 200
def get_space():
    total, used, free = shutil.disk_usage(BASE_DIR)
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

if __name__ == "__main__":
    app.run(host="192.168.11.79", port=5566)
