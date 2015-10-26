BROKER_URL = 'amqp://myacc:mypw@{0}/myvhost'.format("192.168.0.135")

# default RabbitMQ backend
CELERY_RESULT_BACKEND = 'amqp://'

CELERY_IMPORTS = ("celerytasks")