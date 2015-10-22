from celery import Celery
import celeryconfig

def create_celery_app():
    celery = Celery(__name__)
    celery.config_from_object(celeryconfig)
    return celery

celery = create_celery_app()

if __name__ == "__main__":
    celery.start()
