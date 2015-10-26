import netifaces as ni

BROKER_URL = 'amqp://myacc:mypw@{0}/myvhost'.format(ni.ifaddresses('eth0')[2][0]['addr'])
CELERY_RESULT_BACKEND = 'amqp://'
