import flask_session
import os
from threading import Thread
from flask import Flask, redirect, render_template, session, send_from_directory, request, send_file

print(os.path.abspath("./templates/"))
app = Flask(__name__, template_folder=os.path.abspath("./templates/"))
app.config["SESSION_TYPE"] = "filesystem"
flask_session.Session(app)


class HTTP_Server:
    @staticmethod
    @app.get("/")
    async def index():
        if "user" not in session or not session['user']:
            return redirect("/login")
        return render_template("index.html")

    @staticmethod
    @app.get("/login")
    async def login():
        if "user" in session and session['user']:
            return redirect("/")
        return render_template("login.html")

    @staticmethod
    @app.get("/script/<name>")
    async def script(name):
        return send_from_directory(f"./../templates/script/", name, as_attachment=True)

    @staticmethod
    @app.get("/style/<name>")
    async def style(name):
        return send_from_directory(f"./../templates/style/", name, as_attachment=True)

    @staticmethod
    @app.before_request
    async def before_request():
        print(session.__dict__)

    @staticmethod
    def run(host: str = "0.0.0.0", port: int = 80):
        def run_app():
            app.run(host, port)

        t = Thread(target=run_app)
        t.start()
