from celery import Celery
import celeryconfig

def create_celery_app():
    celery = Celery(__name__)
    celery.config_from_object(celeryconfig)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = create_celery_app()

if __name__ == "__main__":
    celery.start()
