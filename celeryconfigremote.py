BROKER_URL = 'amqp://myacc:mypw@{0}/myvhost'.format("192.168.0.135")
CELERY_RESULT_BACKEND = BROKER_URL
