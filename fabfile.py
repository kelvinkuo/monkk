#Fabric file

from fabric.api import local
from fabric.api import run
from fabric.api import cd
from fabric.api import env
from fabric.operations import put

env.hosts = [
    'root@192.168.11.47',
    #'root@192.241.207.26',
    #'root@106.186.116.170',
    #'root@14.18.206.3',
    #'root@110.34.240.58',
    #'root@70.39.189.80',
    #'root@115.85.18.96',

    #42.121.76.137 liyxrl(@WAI
]

def pack(app):
    if app == 'client':
        local('rm -f monclient.tar.gz')
        local('mkdir monkk')
        local('cp mon_client.py daytime.py monkk')
        local('tar -zcf monclient.tar.gz monkk/')
        local('rm -rf monkk')
    elif app == 'supervisor':
        #local('rm -f monsupervisor.tar.gz')
        #local('tar -zcf monsupervisor.tar.gz mon_supervisor.py daytime.py')
        pass

def clean(app):
    if app == 'client':
        #run('ps aux | grep mon_client | grep python | awk \'{print $2}\' | xargs kill -9')
        run('rm -rf /root/monkk')
    elif app == 'supervisor':
        pass

def upload(app):
    if app == 'client':
        put('monclient.tar.gz', '/root/monclient.tar.gz')
        run('tar zxf monclient.tar.gz')
    elif app == 'supervisor':
        pass

def update_env(app):
    local('')
    pass

def launch(app):
    if app == 'client':
        run('ls')
        with cd('/root/monkk'):
            run('ls')
            #run('nohup python mon_client.py 1>/dev/null 2>err.log &')
    elif app == 'supervisor':
        pass

def afterrun(app):
    pass

def install_pip_env():
    ''' make sure pip virtualenv is ready '''
    run()

def deploy(app):
    #local
    pack(app)
    #remote
    clean(app)
    upload(app)
    update_env(app)
    launch(app)
    afterrun(app)

