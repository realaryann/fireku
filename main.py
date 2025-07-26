from flask import Flask, render_template, request, redirect, flash, url_for
import logging
import ipaddress
import subprocess

app = Flask(__name__)
app.secret_key="test"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

FIRESTICK_IP = None

KEYS = {
    "up": 19,
    "down": 20,
    "left": 21,
    "right": 22,
    "select": 23,
    "back": 4,
    "home": 3,
    "menu": 82,
    "play_pause": 85,
    "volup": 24,
    "voldown": 25,
    "mute": 164,
    "power": 26.
}

def verify_ipv4(FIRESTICK_IP) -> bool:
    FIRESTICK_IP=FIRESTICK_IP.strip()
    try:
        ipaddress.IPv4Address(FIRESTICK_IP)
        logger.info("IPV4 address syntax verified")
        return True
    except Exception as e:
        logger.error(f"{Exception}: IPV4 address syntax not verified")
        return False


def establish_connection(FIRESTICK_IP) -> bool:
    res = subprocess.run(["adb", "connect", FIRESTICK_IP], capture_output=True)
    if res.returncode != 0 or ("failed" in str(res.stdout)):
        logger.error("adb connect failed")
        return False
    return True


def send_keycode(keycode):
    res = subprocess.run(["adb", "shell", "input", "keyevent", str(keycode)], capture_output=True)


@app.route('/remote', methods=["GET", "POST"])
def remote_page():
    if FIRESTICK_IP == None:
        return redirect(url_for("index"))

    if request.method == "POST":
        if establish_connection(FIRESTICK_IP):
            logger.debug(f"Sending Key: {request.form['button']}")
            send_keycode(KEYS[request.form["button"]])
    
    return render_template("firetv.html")

@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        #button = request.form.get("button")
        #TODO Clean the IP, raise errors if bad
        global FIRESTICK_IP 
        FIRESTICK_IP = request.form["ip"] 
        if FIRESTICK_IP == None:
            flash("You must first connect to your Fire TV with a valid IP")
            return redirect("/")
        else:
            if verify_ipv4(FIRESTICK_IP):
                return redirect(url_for("remote_page"))
            else:
                flash("IPV4 address syntax is incorrect")
                return redirect("/")
    return render_template("remote.html")


if __name__ == "__main__":
    app.run()