from project.server.extensions import celery


@celery.task
def dummy_task():
    return "OK"
