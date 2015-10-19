import os
import novaclient.client

def getnovaclient():
    config = {'user':os.environ['OS_USERNAME'],
              'api_key':os.environ['OS_PASSWORD'],
              'project_id':os.environ['OS_TENANT_NAME'],
              'auth_url':os.environ['OS_AUTH_URL']
              }
    return novaclient.client.Client('2', **config)
