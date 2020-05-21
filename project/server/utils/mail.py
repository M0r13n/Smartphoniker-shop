from kombu.exceptions import OperationalError

from project.server.models import MailLog
from project.tasks import send_email_task


def send_email(msg):
    log = MailLog.create(recipients="; ".join(msg['to']))
    try:
        mail = send_email_task.apply_async(args=[msg, log.id])
        return mail
    except OperationalError:
        pass

    return None
