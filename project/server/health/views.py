from flask import Blueprint, current_app
from sqlalchemy.exc import OperationalError

from project.common.stats import celery_status, redis_status
from project.server import db

health_bp = Blueprint("health", __name__, url_prefix='/status')


@health_bp.route('/')
def flask():
    return "OK", 200


@health_bp.route('/db')
def database():
    try:
        db.session.execute('SELECT 1')
    except OperationalError as e:
        current_app.logger.error(e)
        return "DOWN", 400
    return "OK", 200


@health_bp.route('/celery')
def celery():
    status = celery_status()
    if not status:
        return "DOWN", 400
    return "OK", 200


@health_bp.route('/redis')
def redis():
    status = redis_status()
    if not status:
        return "DOWN", 400
    return "OK", 200
