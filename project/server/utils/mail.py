from project.server.models import MailLog
from project.tasks import send_email_task


def send_email(msg):
    log = MailLog.create(recipients="; ".join(msg['to']))
    mail = send_email_task.apply_async(args=[msg, log.id])
    return mail
