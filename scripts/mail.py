import smtplib
import ssl
from email.message import EmailMessage
from flask import render_template


def send_mail(to: str, template_path: str, variables: dict):
    msg = EmailMessage()
    msg.set_content(render_template(template_path, **variables))
    msg['Subject'] = "Hello Underworld from Python Gmail!"
    msg['From'] = "register.hash@gmail.com"
    msg['To'] = to

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login("register.hash@gmail.com", "sbftadlqusbomdbi")
        server.send_message(msg, from_addr="register.hash@gmail.com", to_addrs=to)
