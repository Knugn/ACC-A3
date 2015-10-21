import os
import novautil
import paramiko
from celeryapp import celery

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
startceleryscript = """\
#!bin/bash
for i in {1..{0}}
do
    celery -A celerytasks.py -n one.%h &
done
""".format(n_celery_workers_per_vm)
worker_name_prefix = 'RymanA3-worker'
workers = []

def getworkernamegen():
    return ((worker_name_prefix + str(i)) for i in xrange(n_worker_vms))

def spawnworkers(namegen, **kwargs):
    for name in namegen:
        w = nc.servers.create(name, **kwargs)
        ip = w.networks.values()[0]
        print "Created", w, "with ip", ip
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username='ubuntu', password = workerconfig['admin_pass'])
        workers.append(w)
    return workers

def start():
    spawnworkers(getworkernamegen(), **workerconfig)
    return

def stop():
    celery.control.broadcast('shutdown') # shutdown all workers
    for w in workers:
        w.delete()
    return

def getworkers():
    return workers

if __name__ == "__main__":
    start()

