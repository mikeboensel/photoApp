web: gunicorn config.wsgi:application
worker: celery worker --app=struggla.taskapp --loglevel=info
