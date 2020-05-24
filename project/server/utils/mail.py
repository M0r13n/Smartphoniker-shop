from kombu.exceptions import OperationalError

from project.server.models import MailLog
from project.server.models.mail_log import MailStatus
from project.tasks import send_email_task


def send_email(msg):
    log = MailLog.create(recipients="; ".join(msg['to']))
    try:
        mail = send_email_task.apply_async(args=[msg, log.id])
        return mail
    except OperationalError as e:
        log.err_traceback = str(e)
        log.status = MailStatus.ERROR

    return None
