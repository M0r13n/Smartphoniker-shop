# project/server/user.py
import datetime
import enum

from flask_login import UserMixin

from project.server import db
from .crud import CRUDMixin


class MailStatus(enum.Enum):
    PENDING = 1
    IN_PROGRESS = 2
    SUCCESS = 3
    MAX_RETRIES_EXCEEDED = 4
    ERROR = 5


class MailLog(UserMixin, CRUDMixin, db.Model):
    __tablename__ = "mail_log"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    subject = db.Column(db.String(255), nullable=True)
    recipients = db.Column(db.Text())
    retries = db.Column(db.Integer, default=0)

    status = db.Column(db.Enum(MailStatus), default=MailStatus.PENDING)
    err_traceback = db.Column(db.Text())

    def __repr__(self):
        return f"<MailLog: [Status:{self.status}]>"
