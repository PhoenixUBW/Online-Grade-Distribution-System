from flask import *

app = Flask(__name__)

logged_in = False


def login_required(func):
    def wrapper(*args, **kwargs):
        if logged_in == True:
            return func(*args, **kwargs)
        else:
            flash("you need to login first.")
            return redirect(url_for("login"))
    return wrapper

@app.route("/")
@login_required
def homepage():
    return render_template("home.html")

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    return redirect(url_for("welcome"))


if __name__ == "__main__":
    app.run(debug=True)
