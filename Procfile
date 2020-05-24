web: python wsgi.py
worker: celery worker -A project.server.celery_app:app --loglevel=info
#postdeploy: python manage.py dev-db