from flask import Flask, render_template, request, redirect
import logging
import subprocess

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

KEYS = {
    "up": 19,
    "down": 20,
    "left": 21,
    "right": 22,
    "select": 23,
    "back": 4,
    "home": 3,
    "menu": 82,
    "play_pause": 85
}

def send_key(keycode, FIRESTICK_IP):
    subprocess.run(["adb", "connect", FIRESTICK_IP], capture_output=True)
    subprocess.run(["adb", "shell", "input", "keyevent", str(keycode)], capture_output=True)


@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        button = request.form.get("button")
        #TODO Clean the IP, raise errors if bad
        FIRESTICK_IP = request.form["ip"]    
        if button in KEYS:
            try:
                send_key(KEYS[button], FIRESTICK_IP)
            except Exception as e:
                logger.error(f"{e}: Not able to communicate message to Fire TV")

        return redirect('/')
    return render_template("remote.html")


if __name__ == "__main__":
    app.run()