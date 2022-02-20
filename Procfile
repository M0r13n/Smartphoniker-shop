web: python wsgi.py
worker: celery -A project.server.celery_app:app worker --loglevel=info
# Always run DB migrations and import new SVGs
postdeploy: python manage.py db upgrade && python manage.py load-svg
