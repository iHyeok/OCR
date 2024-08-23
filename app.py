from flask import Flask, redirect, render_template, url_for, request, flash
from DB_handler import DBModule

app=Flask(__name__)
app.secret_key = ''

db=DBModule()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/list")
def post_list():
    pass

@app.route("/post/<int:pid>")
def post(pid):
    pass

@app.route("/login")
def login():
    pass

@app.route("/signin")
def signin():
    return render_template("signin.html")


@app.route("/login_done")
def login_done():
    pass

@app.route("/signin_done", methods = ["get"])
def signin_done():
    email = request.args.get("email")
    uid = request.args.get("id")
    pwd = request.args.get("pwd")
    name = request.args.get("name")

    if db.signin(_id_ = uid, pwd = pwd, name = name, email = email):    return redirect(url_for("index"))
    else:
        flash("이미 존재하는 아이디 입니다")
        return redirect(url_for("signin"))



@app.route("/user/<uid>")
def user(uid):
    pass

@app.route("/write")
def write():
    pass

@app.route("/write_done", methods = ["GET"])
def write_done():
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)