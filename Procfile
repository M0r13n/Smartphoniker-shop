web: python wsgi.py
worker: celery worker -A project.server.celery_app:app --loglevel=info
# Always run DB migrations and import new SVGs
postdeploy: python manage.py db upgrade && python manage.py load-svg
