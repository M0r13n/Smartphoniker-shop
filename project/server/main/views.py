# project/server/main/views.py


from flask import render_template, Blueprint, jsonify

from project.common.email.message import make_html_mail
from project.tasks import send_email_task

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def home():
    return render_template("main/home.html")


@main_blueprint.route("/mail")
def send_mail():
    html_body = render_template("mails/example_mail.html", user="Tim")
    msg = make_html_mail(to_list=["leon.morten@gmail.com", "leonrichter@fastmail.com"], from_address="anfrage@smartphoniker.de",
                         subject="Ich will das hier html drinnen ist", html_body=html_body, text_body="Das ist text!!!!!!11111elf!!!!")
    mail = send_email_task.apply_async(args=[msg])
    print(mail)
    return jsonify(dict(status="Task received"))
