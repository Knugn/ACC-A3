import netifaces as ni

# default RabbitMQ broker
#BROKER_URL = 'amqp://'
BROKER_URL = 'amqp://myacc:mypw@{0}/myvhost'.format(ni.ifaddresses('eth0')[2][0]['addr'])

# default RabbitMQ backend
CELERY_RESULT_BACKEND = 'amqp://'

CELERY_IMPORTS = ("celerytasks")
