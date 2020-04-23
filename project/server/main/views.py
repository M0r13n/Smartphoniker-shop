# project/server/main/views.py


from flask import render_template, Blueprint

from project.tasks import send_email_task

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def home():
    from project.common.email.message import EmailMessage
    msg = EmailMessage(
        subject="I mag Tests",
        body="Das stimmt sehr wohl!",
        from_email="anfrage@smartphoniker.de",
        to=["leon.morten@gmail.com"],
        bcc=["leonrichter@gmail.com"]
    )

    print(send_email_task.apply_async(args=[msg.to_dict()]))
    return render_template("main/home.html")
