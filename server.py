from flask import Flask, request, jsonify, render_template
from pathlib import Path
import shutil
import platform
app = Flask(__name__)

if platform.system() == "Windows":
    # Local development path
    BASE_DIR = Path(r"C:\Users\admin.AD\PycharmProjects\test\screenshots")
else:
    # Linux / Docker path
    BASE_DIR = Path("/app/screenshots")

BASE_DIR.mkdir(parents=True, exist_ok=True)

# How long to keep screenshots (in minutes)
RETENTION_MINUTES = 5
host = platform.uname()[1]

def get_folder_size(files):
    """Return total size (MB) of all given files."""
    return sum(f.stat().st_size for f in files) / (1024 * 1024)

@app.route("/data")
def data():
    """Return disk usage info in JSON for the gauge."""
    return jsonify(get_space())

@app.route("/", methods=["GET", "POST"])
def index():
    info = get_space()
    if request.method == "GET":
        data = {}
        sum = 0
        for host_dir in BASE_DIR.iterdir():
            if host_dir.is_dir():
                host_info = {}
                total_host_size = 0.0

                for date_dir in host_dir.iterdir():
                    if date_dir.is_dir():
                        files = list(date_dir.glob("*.jpg"))
                        size_mb = get_folder_size(files)
                        sum = sum + size_mb
                        total_host_size += size_mb

                        host_info[date_dir.name] = {
                            "files": [f.name for f in files],
                            "size": f"{size_mb:.2f} MB",
                            "count": len(files),
                        }

                data[host_dir.name] = {
                    "dates": host_info,
                    "total_size": f"{total_host_size:.2f} MB",
                }



        return render_template("index.html", data=data, sum=round(sum, 2), info=info, host=host)



@app.route("/upload", methods=["POST"])
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


# if __name__ == "__main__":
#
#     app.run(host="0.0.0.0", port=5003)
