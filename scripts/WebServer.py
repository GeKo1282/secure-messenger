import base64
import hashlib
import json
import logging
import random
import flask_session
import os
import string
from hashlib import sha256
from scripts.cypher import Cipher
from scripts.mail import send_mail
from scripts.database import Database
from threading import Thread
from flask import Flask, redirect, render_template, session, send_from_directory, request

print(os.path.abspath("./templates/"))
app = Flask(__name__, template_folder=os.path.abspath("./templates/"), static_folder=os.path.abspath("./static/"))
app.config["SESSION_TYPE"] = "filesystem"
app.app_context()
flask_session.Session(app)

logging.getLogger('werkzeug').disabled = True


class HTTP_Server:
    def __init__(self, cipher, hostname, logger: logging.Logger = None):
        app.logger.handlers.clear()
        if logger:
            app.logger.addHandler(logger)
        app.config['cipher']: Cipher = cipher
        app.config['hostname'] = hostname

    @staticmethod
    @app.get("/")
    async def index():
        if "user" not in session or not session['user']:
            return redirect("/login")
        return render_template("index.html")

    @staticmethod
    @app.route("/login", methods=["GET", "POST"])
    async def login():
        if request.method == "GET":
            if "user" in session and session['user']:
                return redirect("/")
            login = request.args.get("login", None)
            return render_template("login.html", login=base64.b64decode(login).decode() if login else "")
        else:
            try:
                data = json.loads(request.data.decode())
            except json.JSONDecodeError:
                data = json.loads(app.config['cipher'].decrypt(request.data.decode()))

            database = Database.get_database_by_name("users")

            if not data.get("email_check", False):
                return json.dumps({"success": database.check_if_exists("users", "email=:email AND password=:password ",
                    {"email": data['email'], "password": hashlib.sha256(data['password'].encode()).hexdigest()}), "ev": True})

            if not database.check_if_exists("users", "email=:email", {"email": data['email']}):
                return json.dumps({"success": False, "message": "INCORRECT E-MAIL!"})

            if not database.check_if_exists("users", "email=:email AND email_verified=:ev", {"email": data['email'], "ev": True}):
                return json.dumps({"success": False, "message": "YOU MUST VERIFY YOUR EMAIL FIRST!"})

            return json.dumps({"success": True})

    @staticmethod
    @app.route("/register", methods=['GET', 'POST'])
    async def register():
        if request.method == "GET":
            if "user" in session and session['user']:
                return redirect("/login")
            return render_template("register.html")
        else:
            data = json.loads(app.config['cipher'].decrypt(request.data.decode()))
            user_db = Database.get_database_by_name('users')
            user = user_db.check_if_exists('users', "email=:email", {"email": data['email']})
            if user:
                return json.dumps({
                    "header": "This email is taken!",
                    "sub": "This email was already taken by someone else. If this is your e-mail"
                           f" ({data['email']}) you might request password reset <a href='/forgotten-password'>here</a>."
                           f" If you think that is incorrect or someone else took your e-mail, please contact us at"
                           f" <a href='mailto:support.hash@gmail.com'>support.hash@gmail.com</a>."
                })

            def generate_unique(db_field: str, gen_func, *, additional_checks: dict = None):
                if not additional_checks:
                    additional_checks = {}

                random_result = gen_func()
                additional_checks_str = "".join([f" AND {var}=:{var}" for var in additional_checks.keys()])
                while user_db.check_if_exists('users', f"{db_field}=:{db_field}{additional_checks_str}",
                                              {db_field: random_result, **additional_checks}):
                    random_result = gen_func()
                return random_result

            uuid = generate_unique('uuid', lambda: "".join(
                [str(random.randint(1, 9))] + [str(random.randint(0, 9)) for _ in range(15)]))
            tag = generate_unique('tag', lambda: "".join([str(random.randint(0, 9)) for _ in range(4)]),
                                  additional_checks={"username": data['username']})
            code = "".join([random.choice(string.ascii_letters + string.digits + "_.") for _ in range(128)])
            user_db.insert('users', [{'uuid': uuid, 'email': data['email'],
                                      'password': sha256(data['password'].encode()).hexdigest(),
                                      'username': data['username'], 'tag': tag,
                                      'email_verified': False, 'verification_code': code}])

            def send(flask_app):
                send_mail(data['email'], 'Hash - Registration confirmation', 'register.hash@gmail.com',
                          'email_template.html', {"username": data['username'],
                                                  'url': f'{app.config["hostname"]}/register-confirm/{base64.b64encode(uuid.encode()).decode()}/{code}'},
                          flask_app)

            t = Thread(target=send, args=(app,))
            t.start()

            return json.dumps({
                "header": "Successfully created account!",
                "sub": "We'll now send you an confirmation e-mail to your address"
                       f" ({data['email']}). Please confirm your account and log-in"
                       f" using button below. If you have not received our email after a few minutes,"
                       f" check your spam folder or request another.",
                "buttons": [{
                    "content": "Log in!",
                    "onclick": f"window.location.replace(`/login?login={base64.b64encode(data['email'].encode()).decode()}`)",
                    "style": "background: var(--green-button);"
                }, {
                    "content": "Request another email!",
                    "onclick": f"request_email({data['email']})",
                    "style": "background: var(--red-button);"
                }]
            })

    @staticmethod
    @app.post("/request-verification")
    async def request_verification():
        data = json.loads(request.data.decode())
        database = Database.get_database_by_name('users')
        verified, code, uuid = database.fetch("users", "uuid=:uuid", {"email": data['email']},
                                              columns="email_verified, verification_code, uuid", fetchall=False)
        if verified:
            return json.dumps({
                "header": "Already verified!",
                "sub": f"Your account ({data['email']}) is already verified! If you think that this is incorrect contact"
                       f" us at <span class='email'>support.hash@gmail.com</span>. Otherwise login to your account"
                       f" using button below.",
                "buttons": [{
                    "content": "Log in!",
                    "onclick": f"window.location.replace('/login?login={base64.b64encode(data['email']).decode()}')",
                    "style": "background: var(--green-button);"
                }]
            })

        if code is None:
            code = "".join([random.choice(string.ascii_letters + string.digits + "_.") for _ in range(128)])

        database.update("users", "uuid=:uuid", {"uuid": uuid}, {"verification_code": code})

        def send(flask_app):
            send_mail(data['email'], 'Hash - Registration confirmation', 'register.hash@gmail.com',
                      'email_template.html', {"username": data['username'],
                                              'url': f'{app.config["hostname"]}/register-confirm/{base64.b64encode(uuid.encode()).decode()}/{code}'},
                      flask_app)

        t = Thread(target=send, args=(app,))
        t.start()

        return json.dumps({
            "header": "Successfully requested verification e-mail!",
            "sub": "We'll now send you an confirmation e-mail to your address"
                   f" ({data['email']}). Please confirm your account and log-in"
                   f" using button below. Be sure to check your <span style='color:red;'>spam</span> folder!",
            "buttons": [{
                "content": "Log in!",
                "onclick": f"window.location.replace('/login?login={base64.b64encode(data['email']).decode()}')",
                "style": "background: var(--green-button);"
            }, {
                "content": "Request another email",
                "onclick": f"request_email('{data['email']}')",
                "style": "background: var(--green-button);"
            }]
        })

    @staticmethod
    @app.get("/register-confirm/<uuid>/<code>")
    async def register_confirm(uuid, code):
        uuid = base64.b64decode(uuid).decode()
        database = Database.get_database_by_name("users")
        obj = database.fetch('users', 'uuid=:uuid', {'uuid': uuid}, fetchall=False,
                             columns="verification_code, email_verified, email")
        if not obj:
            return render_template("verification_page.html", header="Invalid link!",
                                   sub="We are very sorry, but account with this link does not exist. Please go to "
                                       "registration page using button below and fill out registration form. If your "
                                       "account was previously created, but link was incorrect, we will provide you a "
                                       "newly generated one.", email="",
                                   verified=False, exists=False)

        v_code, verified, email = obj
        if v_code != code or verified:
            return render_template("verification_page.html", header="Invalid code!",
                                   sub=f"Your account ({email}) is already verified"
                                       f", or verification code is invalid! Please request new verification e-mail by clicking the button below."
                                       f" If you think that this is incorrect contact  us at <span class='email'>support.hash@gmail.com</span>."
                                       f" Otherwise login to your account using button below.", email=email,
                                   verified=False, exists=True)

        database.update("users", "uuid=:uuid", {"uuid": uuid}, {"email_verified": True, "verification_code": None})
        return render_template("verification_page.html", header="Successfully verified!",
                               sub=f"Your account ({email}) has been successfully verified!"
                                   f" Now you can login to your new account by clicking the button below.",
                               email=email, verified=True, exists=True)

    @staticmethod
    @app.get("/forgotten-password")
    async def forgot_password():
        if "user" in session and session['user']:
            return redirect("/login")
        return render_template("forgot_password.html")

    @staticmethod
    @app.get("/script/<name>")
    async def script(name):

        return send_from_directory(f"./../templates/script/", name, as_attachment=True)

    @staticmethod
    @app.get("/style/<name>")
    async def style(name):
        return send_from_directory(f"./../templates/style/", name, as_attachment=True)

    @staticmethod
    @app.get("/resource/<name>")
    async def resource(name):
        if name == "encryption-data":
            return json.dumps({
                "key": app.config['cipher'].get_public_key(),
                "separator": app.config['cipher'].separator,
                "max_message_length": app.config['cipher'].get_max_message_length()
            })
        else:
            return ""

    @staticmethod
    @app.before_request
    async def before_request():
        pass

    @staticmethod
    def run(host: str = "0.0.0.0", port: int = 80):
        def run_app():
            app.run(host, port)

        t = Thread(target=run_app)
        t.start()
