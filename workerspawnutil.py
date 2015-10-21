import os
import novautil

nc = novautil.getnovaclient()
workerconfig = {
    'image' : nc.images.find(name='Ryman Celery Worker Base').id,
    'flavor' : nc.flavors.find(name='m1.medium').id,
    'network' : nc.networks.find(label='ext-net').id,
    #key_name = nc.keypairs.list().pop().name
    'admin_pass' : os.environ['OS_PASSWORD']
}
n_worker_vms = 1
n_celery_workers_per_vm = 4
worker_name_prefix = 'RymanA3-worker'

def getworkernamegen():
    return ((worker_name_prefix + str(i)) for i in xrange(n_worker_vms))

def spawnworkers(nc, namegen, **kwargs):
    workers = []
    for name in namegen:
        workers.append(nc.servers.create(name, **kwargs))
    return workers

if __name__ == "__main__":
    spawnworkers(nc, getworkernamegen(), **workerconfig)

