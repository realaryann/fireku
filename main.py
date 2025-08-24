from flask import Flask, render_template, request, redirect, flash, url_for
import ast
from connection import *
from keydefine import *

# Flask settings
app = Flask(__name__)
app.secret_key="test"


Conn = ConnectionHandler()


def cycle_ips():
    # Must find out whether IP is Fire TV or Roku
    global FIRESTICK_IP
    global ROKU_IP
    """
    # Check for Fire TV
    if Conn.firetv_establish_connection(potential_ip):
        FIRESTICK_IP=potential_ip
        return "firetv"
    """
    # Check for Roku
    Conn.discover_roku()
    """
    elif Conn.roku_establish_connection(potential_ip):
        ROKU_IP=potential_ip
        return "roku"
    """

@app.route("/choose_devices", methods=["GET","POST"])
def choose_devices():
    global ROKU_IP, FIRESTICK_IP
    if request.method == "POST":
        device_details = ast.literal_eval(request.form["device"])
        if device_details["type"] == "roku":
            ROKU_IP = device_details["ip"]
            return redirect(url_for("roku_page"))
        
        elif device_details["type"] == "firetv":
            return redirect(url_for("firetv_page"))

    ret = cycle_ips()
    return render_template("choose_devices.html", devices=Conn.device_ip_name)


@app.route("/roku", methods=["GET", "POST"])
def roku_page():
    if request.method == "POST":
        if request.form['button'] in ROKU_KEYS:
            logger.debug(f"Sending Key: {request.form['button']}")
            Conn.roku_send_keycode(ROKU_IP=ROKU_IP, keycode=request.form['button'])

    return render_template("roku.html")


@app.route('/remote', methods=["GET", "POST"])
def firetv_page():
    if request.method == "POST":
        logger.debug(f"Sending Key: {request.form['button']}")
        Conn.firetv_send_keycode(FIRE_KEYS[request.form["button"]])
    
    return render_template("firetv.html")


@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        return redirect(url_for("choose_devices"))
                        
    return render_template("index.html")


if __name__ == "__main__":
    app.run()