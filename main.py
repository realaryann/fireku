from flask import Flask, render_template, request, redirect, flash, url_for
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
    potential_ip = request.form["ip"]
    if potential_ip == None:
        flash("You must first connect to your Fire TV / Roku with a valid IP")
    else:
        if Conn.verify_ipv4(potential_ip):
            # Check for Fire TV
            if Conn.firetv_establish_connection(potential_ip):
                FIRESTICK_IP=potential_ip
                return "firetv"
            # Check for Roku
            elif Conn.roku_establish_connection(potential_ip):
                ROKU_IP=potential_ip
                return "roku"
            else:
                flash(f"Unable to establish connection to {potential_ip}")
                return ""
        else:
            flash("IPV4 address syntax is incorrect")
            return ""


@app.route("/roku", methods=["GET", "POST"])
def roku_page():
    if request.method == "POST":
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
        ret = cycle_ips()
        if ret == "roku":
            return redirect(url_for("roku_page"))
        elif ret == "firetv":
            return redirect(url_for("firetv_page"))
        else:
            return redirect("/")
    return render_template("index.html")


if __name__ == "__main__":
    app.run()