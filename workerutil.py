import os
import novautil
import paramiko
#from celeryapp import celery
import time

nc = novautil.getnovaclient()
workerconfig = {
    'image' : nc.images.find(name='Ryman Celery Worker Base').id,
    'flavor' : nc.flavors.find(name='m1.medium').id,
    'network' : nc.networks.find(label='ext-net').id,
    'key_name' : 'rymanserverkey'#nc.keypairs.list().pop().name
    #'admin_pass' : os.environ['OS_PASSWORD']
}
#n_worker_vms = 1
n_celery_workers_per_vm = 4
vm_name_prefix = 'RymanA3-worker'
name_count = 0
vms = []

def getworkernamegen():
    return ((worker_name_prefix + str(i)) for i in xrange(n_worker_vms))

def next_vm_name():
    global name_count
    name_count += 1
    return vm_name_prefix + str(name_count)

def create_worker_vm(name=None, kwargs=workerconfig): 
    global nc
    global vms
    if not name:
        name = next_vm_name()
    vm = nc.servers.create(name, **kwargs)
    vms.append(vm)
    return vm

def get_network(vm, netname):
    global nc
    while True:
        nets = nc.servers.ips(vm)
        if netname in nets:
            return nets[netname]

def start_celery_workers_remote(ssh): 
    # TODO: copy neccesary scripts and start celery workers
    # broker is assumed to be located on the machine running this function
    print 'Starting celery workers on remote machine with ssh', ssh
    with ssh.open_sftp() as sftp:
        print 'Uploading required celery worker files with sftp', sftp
        sftp.put('celeryconfigremote.py', 'celeryconfig.py')
        for file_name in ['celerytasks.py', 'celeryapp.py', 'swiftutil.py', 'tweetutil.py']:
            sftp.put(file_name, file_name)
    #print 'Invoking celery startup script'
    (stdin, stdout, stderr) = ssh.exec_command("celery worker -A celerytasks.py -n c0.%h --app=celeryapp:celery &")
    return

def spawn_worker_vm(name=None):
    global nc
    print '-= Spawning worker VM =-'
    vm = create_worker_vm(name)
    print 'name:', vm.name
    #vm_ip = vm.networks.values()[0]
    print 'Waiting for VM network ...'
    vm_ip = get_network(vm, 'ACC-Course-net')[0]['addr']
    print 'ip:' , vm_ip
    print 'Establishing ssh connection to VM with ip:', vm_ip
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        while True:
            try:
                ssh.connect(vm_ip, username='ubuntu', key_filename = 'rymanserverkey.pem', timeout=60)
                break
            except:
                print 'ssh connection failed, trying again in 3 seconds...'
                time.sleep(3)
        print 'ssh connection established successfully'
        start_celery_workers_remote(ssh)
    print 'Successfully spawned worker VM'
    return vm

def add_worker_vms(n=1):
    for i in xrange(n):
        spawn_worker_vm()
    return

#def remove_worker_vm(n=1): pass
def clear_worker_vms():
    kill_worker_vms()
    global name_count
    name_count = 0
    return

def kill_worker_vms():
    for vm in list_worker_vms():
        vm.delete()
    return

def list_worker_vms():
    global nc
    return filter(lambda serv: serv.name.startswith(vm_name_prefix), nc.servers.list())

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
    for vm in vms:
        vm.delete()
    return

#def get_vms():
#    return vms

#if __name__ == "__main__":
#    start()

