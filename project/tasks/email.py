import functools

from celery.exceptions import MaxRetriesExceededError, Retry
from flask import current_app

from project.common.email.backend import EmailBackend
from project.common.email.message import EmailMessage, EmailMultiAlternatives
from project.server.extensions import celery

MAX_TRIES = 10
DELAYS = [30, 60, 120, 300, 600, 1800, 3600, 3600, 7200]


@celery.task(name='send_email', bind=True, retry=False)
def send_email_task(task, email):
    attempt = task.request.retries + 1
    # update state
    task.update_state(state='PROGRESS', meta={'retries': attempt, 'max_retries': MAX_TRIES})

    # send mail and retry with exponential retries timeout
    try:
        _send_mail(email)
    except (MaxRetriesExceededError, Retry):
        delay = DELAYS[task.request.retries]
        try:
            task.retry(countdown=delay, max_retries=(MAX_TRIES - 1))
        except MaxRetriesExceededError:
            task.update_state(state='FAILED', meta={'retries': attempt, 'max_retries': MAX_TRIES})
        except Retry:
            raise
    else:
        current_app.logger.info('Email sent successfully')


def validate(func):
    """
    This decorator is used to pre-validate email data.
    """

    @functools.wraps(func)
    def wrapper(mail_dto: dict, *args, **kwargs):
        if not mail_dto.get('from_email'):
            mail_dto['from_email'] = current_app.config['DEFAULT_MAIL_SENDER']

        return func(mail_dto, *args, **kwargs)

    return wrapper


@validate
def _send_mail(mail_dto: dict):
    """
    Send a email.
    This is a normal, BLOCKING, Python method.
    You are mostly not wanting to call this directly, but rather through celery or in a separate thread.
    """
    conf = current_app.config

    if mail_dto.get('html', False) and mail_dto.get('text_body', False):
        msg = EmailMultiAlternatives.from_dict(mail_dto)
        msg.attach_alternative(mail_dto.get('text_body'), 'text/plain')
    else:
        msg = EmailMessage.from_dict(mail_dto)

    with EmailBackend(timeout=30, host=conf['MAIL_SERVER'], port=conf['MAIL_PORT'], username=conf['MAIL_USERNAME'],
                      password=conf['MAIL_PASSWORD'], use_tls=conf['MAIL_USE_TLS'], use_ssl=conf['MAIL_USE_SSL']) as conn:
        msg.connection = conn
        msg.send()
