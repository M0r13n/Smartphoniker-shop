web: python wsgi.py
worker: celery worker -A project.server.celery_app:app --loglevel=info
# Always run DB migrations
postdeploy: python manage.py db upgrade
