from flask import Flask, render_template, request, redirect, flash, url_for
from connection import *
from keydefine import *

# Flask settings
app = Flask(__name__)
app.secret_key="test"


Conn = ConnectionHandler()


@app.route('/remote', methods=["GET", "POST"])
def remote_page():
    if request.method == "POST":
            logger.debug(f"Sending Key: {request.form['button']}")
            Conn.send_keycode(KEYS[request.form["button"]])
    
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
            if Conn.verify_ipv4(FIRESTICK_IP):
                if Conn.establish_connection(FIRESTICK_IP):
                    return redirect(url_for("remote_page"))
                else:
                    flash(f"Unable to establish connection to {FIRESTICK_IP}")
                    return redirect('/')
            else:
                flash("IPV4 address syntax is incorrect")
                return redirect("/")
            
    return render_template("remote.html")


if __name__ == "__main__":
    app.run()