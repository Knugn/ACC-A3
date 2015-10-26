import os
import novautil
import paramiko
import time
from celeryapp import celery

debug = False
nc = novautil.getnovaclient()
workerconfig = {
    'image' : nc.images.find(name='Ryman A3 Worker Core').id,
    'flavor' : nc.flavors.find(name='m1.medium').id,
    'network' : nc.networks.find(label='ext-net').id,
    'key_name' : 'rymanserverkey'#nc.keypairs.list().pop().name
    #'admin_pass' : os.environ['OS_PASSWORD']
}
n_celery_workers_per_vm = 2
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

def ssh_exec_check_failure(ssh, command):
    global debug
    (stdin, stdout, stderr) = ssh.exec_command(command)
    if debug:
        first = True
        for part in command.split('\n'):
            if first:
                print '\t>>'+part
                first = False
            else:
                print '\t  '+part
        for line in stdout.readlines():
            print '\t'+line,
    failure = False
    first = True
    for line in stderr.readlines():
        if first:
            print 'Failed to execute command:'
            print command
            first = False
            failure = True
        print '\t'+line,
    return failure

def start_celery_workers_remote(ssh): 
    # TODO: copy neccesary scripts and start celery workers
    # broker is assumed to be located on the machine running this function
    failure = False
    with ssh.open_sftp() as sftp:
        print 'Uploading required celery worker files with sftp', sftp
        sftp.put('celeryconfigremote.py', 'celeryconfig.py')
        for file_name in ['celerytasks.py', 'celeryapp.py', 'swiftutil.py', 'tweetutil.py']:
            sftp.put(file_name, file_name)
    #print 'Copying environment variables for swift connection and broker connection'
    # TODO: add broker url to environment variables and remove if from celeryconfig
    envcmd = "env"
    for envvar in ['OS_USERNAME', 'OS_PASSWORD', 'OS_TENANT_NAME', 'OS_AUTH_URL']:
        envcmd += " {0}={1}".format(envvar, os.environ[envvar])
    print 'Starting celery workers on remote machine with ssh', ssh
    for i in xrange(n_celery_workers_per_vm):
        if ssh_exec_check_failure(ssh, "{0} celery worker --hostname=c{1}.%h --app=celeryapp:celery --detach".format(envcmd, i)):
            print 'Failed to start celery workers on remote machine.'
            return False
    #for i in xrange(n_celery_workers_per_vm):
    #    ssh.exec_command("{0} celery worker -A celerytasks.py -n c{1}.%h --app=celeryapp:celery &".format(envcmd, i))
    return True

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
    failmsg = ''
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
        if not start_celery_workers_remote(ssh):
            failmsg = ', but failed to start celery workers'
    print 'Successfully spawned worker VM'+failmsg
    return vm

def add_worker_vms(n=1):
    for i in xrange(n):
        spawn_worker_vm()
    return

def clear_worker_vms():
    kill_worker_vms()
    global name_count
    name_count = 0
    return

def stop_worker_vms():
    stop_celery_workers_on_worker_vms()
    kill_worker_vms()

def stop_celery_workers_on_worker_vms(): pass

def kill_worker_vms():
    for vm in list_worker_vms():
        vm.delete()
    return

def list_worker_vms():
    global nc
    return filter(lambda serv: serv.name.startswith(vm_name_prefix), nc.servers.list())

#def stop():
#    celery.control.broadcast('shutdown') # shutdown all workers
#    for vm in vms:
#        vm.delete()
#    return

#def get_vms():
#    return vms

#if __name__ == "__main__":
#    start()

