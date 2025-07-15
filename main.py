from flask import Flask, render_template, request, redirect

app = Flask(__name__)


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

@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        button = request.form.get("button")
        if button in KEYS:
            print("yay")
        return redirect('/')
    return render_template("remote.html")

app.run()