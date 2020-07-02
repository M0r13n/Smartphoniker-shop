from celery.exceptions import MaxRetriesExceededError, Retry
from flask import current_app, render_template
from kombu.exceptions import OperationalError

from project.server.common.email.backend import EmailBackend
from project.server.common.email.message import EmailMultiAlternatives, EmailMessage, make_html_mail
from project.server.extensions import celery
from project.server.models import MailLog
from project.server.models.mail_log import MailStatus

MAX_TRIES = 10
DELAYS = [30, 60, 120, 300, 600, 1800, 3600, 3600, 7200]


def send_email(msg):
    log = MailLog.create(recipients="; ".join(msg['to']), subject=msg['subject'])
    try:
        mail = send_email_task.apply_async(args=[msg, log.id])
        return mail
    except OperationalError as e:
        log.err_traceback = str(e)
        log.status = MailStatus.ERROR

    return None


@celery.task(name='send_email', bind=True, max_retries=None)
def send_email_task(task, email, log_entry_id=None):
    attempt = task.request.retries + 1
    # update state
    task.update_state(state='PROGRESS', meta={'retries': attempt, 'max_retries': MAX_TRIES})
    update_log(log_entry_id, status=MailStatus.IN_PROGRESS, retries=attempt)

    # send mail and retry with exponential retries timeout
    try:
        _send_mail(email)
    except Exception as exc:
        update_log(log_entry_id, status=MailStatus.ERROR, err_traceback=str(exc))
        delay = DELAYS[task.request.retries]
        try:
            task.retry(countdown=delay, max_retries=(MAX_TRIES - 1))
        except MaxRetriesExceededError:
            task.update_state(state='FAILED', meta={'retries': attempt, 'max_retries': MAX_TRIES})
            update_log(log_entry_id, status=MailStatus.MAX_RETRIES_EXCEEDED)
        except Retry:
            raise
    else:
        update_log(log_entry_id, status=MailStatus.SUCCESS)
        current_app.logger.info('Email sent successfully')


def update_log(log_entry_id: int = None, retries: int = None, status: MailStatus = None, err_traceback: str = None):
    if not log_entry_id:
        return

    log = MailLog.query.get(log_entry_id)
    if retries:
        log.retries = retries
    if status:
        log.status = status
    if err_traceback:
        log.err_traceback = err_traceback
    log.save()


def _send_mail(mail_dto: dict):
    """
    Send a email.
    This is a normal, BLOCKING, Python method.
    You are mostly not wanting to call this directly, but rather through celery or in a separate thread.
    """
    conf = current_app.config

    if not mail_dto.get('from_email'):
        mail_dto['from_email'] = current_app.config['DEFAULT_MAIL_SENDER']

    if mail_dto.get('html', False) and mail_dto.get('text_body', False):
        msg = EmailMultiAlternatives.from_dict(mail_dto)
        msg.attach_alternative(mail_dto.get('text_body'), 'text/plain')
    else:
        msg = EmailMessage.from_dict(mail_dto)

    with EmailBackend(timeout=30, host=conf['MAIL_SERVER'], port=conf['MAIL_PORT'], username=conf['MAIL_USERNAME'],
                      password=conf['MAIL_PASSWORD'], use_tls=conf['MAIL_USE_TLS'], use_ssl=conf['MAIL_USE_SSL']) as conn:
        msg.connection = conn
        msg.send()


def notify_shop_about_inquiry(inquiry):
    mail_body = render_template("mails/inquiry.html", email=inquiry.customer.email, description=inquiry.description)
    notification = make_html_mail(
        to_list=current_app.config['NOTIFICATION_MAILS'],
        from_address=current_app.config['MAIL_DEFAULT_SENDER'],
        subject="Neue Anfrage über den Pricepicker",
        html_body=mail_body,
        text_body=mail_body
    )
    send_email(notification)


def notify_shop(order):
    """
    Notify shops that there is a new inquiry
    """
    mail_body = render_template("mails/order.html", order=order)
    html_body = render_template("mails/order_html.html", order=order)
    notification = make_html_mail(
        to_list=current_app.config['NOTIFICATION_MAILS'],
        from_address=current_app.config['MAIL_DEFAULT_SENDER'],
        subject="Neue Anfrage über den Pricepicker<script>alert(1);</script>",
        html_body=html_body,
        text_body=mail_body
    )
    send_email(notification)


def send_confirmation(order):
    """
    Notify customer that we received the order
    """
    mail_body = render_template("mails/confirmation.html")
    confirmation = make_html_mail(
        to_list=[order.customer.email],
        from_address=current_app.config['MAIL_DEFAULT_SENDER'],
        subject="Ihre Anfrage bei Smartphoniker",
        html_body=mail_body
    )
    send_email(confirmation)
