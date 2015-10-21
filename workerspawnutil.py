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
workers = []

def getworkernamegen():
    return ((worker_name_prefix + str(i)) for i in xrange(n_worker_vms))

def spawnworkers(namegen, **kwargs):
    for name in namegen:
        w = nc.servers.create(name, **kwargs)
        ip = w.networks.values()[0]
        print "Created", w, "with ip", ip
        workers.append(w)
    return workers

def start():
    spawnworkers(getworkernamegen(), **workerconfig)
    return

def stop():
    for w in workers:
        w.delete()
    return

def getworkers():
    return workers

if __name__ == "__main__":
    start()

