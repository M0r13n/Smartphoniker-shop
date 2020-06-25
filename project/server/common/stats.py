import typing

from kombu.exceptions import OperationalError
from redis.exceptions import ConnectionError as RedisConnectionError

from project.server.extensions import celery, redis_client


def celery_status() -> typing.Optional[dict]:
    """ Try to get status of celery. Returns None is celery is not active"""
    try:
        i = celery.control.inspect()
        stats = i.stats()
        registered_tasks = i.registered()
        active_tasks = i.active()
        scheduled_tasks = i.scheduled()
        result = {
            'stats': stats,
            'registered_tasks': registered_tasks,
            'active_tasks': active_tasks,
            'scheduled_tasks': scheduled_tasks
        }
        return result
    except OperationalError:
        return None


def redis_status() -> typing.Optional[bool]:
    """ Try to ping redis. Return None on error and True on success. """
    try:
        redis = redis_client.redis
        return redis.ping()
    except RedisConnectionError:
        return None
