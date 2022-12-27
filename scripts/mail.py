import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
from flask import render_template


def send_mail(to: str, subject: str, whom_from: str, template_path: str, variables: dict, flask_app):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = formataddr(("Hash", whom_from))
    msg['To'] = to

    with flask_app.app_context():
        msg.attach(MIMEText(render_template(template_path, **variables), 'html'))
    with open("./static/hash_logo.png", 'rb') as f:
        hash_logo = MIMEImage(f.read())
    hash_logo.add_header("Content-ID", "<logo>")
    msg.attach(hash_logo)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(whom_from, "sbftadlqusbomdbi")
        server.send_message(msg, from_addr=whom_from, to_addrs=to)
