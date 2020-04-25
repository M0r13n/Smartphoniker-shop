# project/server/main/views.py


from flask import render_template, Blueprint, jsonify

from project.common.email.message import make_email
from project.tasks import send_email_task

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def home():
    return render_template("main/home.html")


@main_blueprint.route("/mail")
def send_mail():
    html_body = render_template("mails/example_mail.html", user="Tim")
    msg = make_email(to_list="leon.morten@gmail.com", from_address="anfrage@smartphoniker.de",
                     subject="Ich will das hier html drinnen ist", body=html_body, html=True)
    mail = send_email_task.apply_async(args=[msg.to_dict()])
    print(mail)
    return jsonify(dict(status="Task received"))
