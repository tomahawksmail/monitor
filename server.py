from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from ldap3 import Server, Connection, NTLM, ALL
from pathlib import Path
import os
from dotenv import load_dotenv
import shutil
import platform

app = Flask(__name__)

load_dotenv()

app.secret_key = os.environ.get('SECRET') or "super-secret-key"
host = platform.uname()[1]


if platform.system() == "Windows":
    BASE_DIR = Path(r"C:\Users\admin.AD\PycharmProjects\test\screenshots")
else:
    BASE_DIR = Path("/app/screenshots")
    BASE_DIR.mkdir(parents=True, exist_ok=True)

# ===== LDAP CONFIG =====
DOMAIN_CONTROLLER = os.environ.get('DOMAIN_CONTROLLER')
SERVICE_USER = os.environ.get('DCUSERNAME')  # service account
SERVICE_PASS = os.environ.get('DCPASSWORD')
LDAP_GROUP_DN = "CN=Allow-Monitor,OU=CA_Office_Users,DC=ad,DC=uskoinc,DC=com"


def user_dn(username):
    """Convert 'jdoe' into full DN using service account"""
    server = Server(DOMAIN_CONTROLLER, get_info=ALL)

    try:
        conn = Connection(server,
                          user=SERVICE_USER,
                          password=SERVICE_PASS,
                          authentication=NTLM,
                          auto_bind=True)

        conn.search(
            search_base="DC=ad,DC=uskoinc,DC=com",
            search_filter=f"(sAMAccountName={username})",
            attributes=["distinguishedName"]
        )

        if conn.entries:
            return conn.entries[0].distinguishedName.value

    except Exception as e:
        print("DN lookup failed:", e)

    return None




def ldap_auth(username, password):
    """Check if credentials are valid"""
    server = Server(DOMAIN_CONTROLLER)

    # Need full domain\user for NTLM
    user_ntlm = f"ad\\{username}"

    try:
        conn = Connection(server,
                          user=user_ntlm,
                          password=password,
                          authentication=NTLM)
        return conn.bind()
    except Exception:
        return False


def is_user_in_group(username):
    """Check if user belongs to Allow-Monitor group"""
    dn = user_dn(username)
    if not dn:
        return False

    server = Server(DOMAIN_CONTROLLER, get_info=ALL)

    try:
        conn = Connection(server,
                          user=SERVICE_USER,
                          password=SERVICE_PASS,
                          authentication=NTLM,
                          auto_bind=True)

        conn.search(
            search_base=LDAP_GROUP_DN,
            search_filter=f"(member={dn})",
            attributes=["cn"]
        )

        return len(conn.entries) > 0

    except Exception as e:
        print("Group lookup failed:", e)
        return False




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
            return "Invalid username/password", 401

        # Group check
        if not is_user_in_group(username):
            return "You are not allowed to access this system.", 403

        session["username"] = username
        return redirect(url_for("index"))
    else:
        return render_template('login.html')

    # HTML form
    # return redirect(url_for("login"))


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
def get_folder_size(files):
    """Return total size (MB) of all given files."""
    return sum(f.stat().st_size for f in files) / (1024 * 1024)

if __name__ == "__main__":
    app.run(host="192.168.11.79", port=5566)
