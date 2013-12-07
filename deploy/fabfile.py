#Fabric file

from fabric.api import local
from fabric.api import run
from fabric.api import cd
from fabric.api import env
from fabric.operations import put
from fabric.context_managers import settings
from fabric.context_managers import lcd

env.hosts = [
    #'zhangnu@112.124.10.19:22',
    #'zhangnu@42.121.114.19:22',
    #'zhangnu@114.112.172.219:9191',
    #'zhangnu@54.251.110.86:22',

    'root@14.18.206.3:22',
]

env.passwords = {
    #'zhangnu@112.124.10.19:22': '$eDBi43#',
    #'zhangnu@42.121.114.19:22': '$eDBi43#',
    #'zhangnu@114.112.172.219:9191': '$eDBi43#',
    #'zhangnu@54.251.110.86:22': '',
    'zhangnu@112.124.10.19:22': '$eDBi43#',
}

env.key_filename = '~/.ssh/zhangnu_id_rsa'
def setservers(app):
    if app == 'clientroot':
        env.hosts = [
        'root@192.241.207.26:22',
        'root@106.186.116.170:22',
        'root@14.18.206.3:22',
        'root@110.34.240.58:22',
        ]

        env.passwords = {
        'root@192.241.207.26:22': 'xvovxbetkreb',
        'root@106.186.116.170:22': 'Elementary)(17',
        'root@14.18.206.3:22': 'ofidc.com1010',
        'root@110.34.240.58:22': 'TrevupRAW8at',
        }
    elif app == 'clientzhangnu':
        env.hosts = [
        'zhangnu@112.124.10.19:22',
        #'zhangnu@42.121.114.19:22',
        #'zhangnu@114.112.172.219:9191',
        #'zhangnu@54.251.110.86:9191',
        ]

        env.passwords = {
        'zhangnu@112.124.10.19:22': '$eDBi43#',
        #'zhangnu@42.121.114.19:22': '$eDBi43#',
        #'zhangnu@114.112.172.219:9191': '$eDBi43#',
        #'zhangnu@54.251.110.86:9191': '$eDBi43#',
        }
    elif app == 'supervisor':
        env.hosts = [
        'root@14.18.206.3:22',
        ]

        env.passwords = {
        'root@14.18.206.3:22': 'ofidc.com1010',
        }
    elif app == 'webserver':
        env.hosts = [
        'root@14.18.206.3:22',
        ]

        env.passwords = {
        'root@14.18.206.3:22': 'ofidc.com1010',
        }

def pack(app):
    if app == 'clientroot' or app == 'clientzhangnu':
        with lcd('../client'):
            local('rm -f monclient.tar.gz')
            local('mkdir bin')
            local('cp ../deploy/run_monclient.sh bin')
            local('cp mon_client.py util.py bin')
            local('tar -zcf monclient.tar.gz bin/')
            local('rm -rf bin')
    elif app == 'supervisor':
        with lcd('../supervisor'):
            local('rm -f monsupervisor.tar.gz')
            local('mkdir monsupervisor')
            local('cp ../deploy/run_monsupervisor.sh monsupervisor')
            local('cp mon_supervisor.py config.py util.py monsupervisor')
            local('tar -zcf monsupervisor.tar.gz monsupervisor')
            local('rm -rf monsupervisor')
    elif app == 'webserver':
        with lcd('../webserver'):
            local('rm -f monwebserver.tar.gz')
            local('mkdir monwebserver')
            local('cp ../deploy/run_webserver.sh monwebserver')
            local('cp mon_webserver.py config.py util.py monwebserver')
            local('cp -r static/ monwebserver')
            local('cp -r templates/ monwebserver')
            local('tar -zcf monwebserver.tar.gz monwebserver')
            local('rm -rf monwebserver')


def packwin(app):
    if app == 'client':
        with lcd('../client'):
            local('rm -f monclient.tar')
            local('mkdir bin')
            local('cp ../deploy/run_monclient.bat bin')
            local('cp mon_client.py util.py bin')
            local('tar -cf monclient.tar bin/')
            local('rm -rf bin')


def clean(app):
    if app == 'clientroot':
        #kill mon_client
        with settings(warn_only=True):
            run('ps aux | grep mon_client | grep python | awk \'{print $2}\' | xargs kill -9')
            run('rm -rf /root/monkk/bin')
    elif app == 'clientzhangnu':
        with settings(warn_only=True):
            run('ps aux | grep mon_client | grep python | awk \'{print $2}\' | xargs kill -9')
            run('rm -rf /home/zhangnu/monkk/bin')
    elif app == 'supervisor':
        with settings(warn_only=True):
            run('ps aux | grep mon_supervisor.py | grep python | awk \'{print $2}\' | xargs kill -9')
            run('rm -rf /root/monsupervisor')
    elif app == 'webserver':
        with settings(warn_only=True):
            run('ps aux | grep mon_webserver.py | grep python | awk \'{print $2}\' | xargs kill -9')
            run('rm -rf /root/monwebserver')


def upload(app):
    if app == 'clientroot':
        put('monclient.tar.gz', '/root/monkk/monclient.tar.gz')
        with cd('monkk'):
            run('tar zxf monclient.tar.gz')
    elif app == 'clientzhangnu':
        with lcd('../client'):
            put('monclient.tar.gz', '/home/zhangnu/monkk/monclient.tar.gz')
        with cd('/home/zhangnu/monkk'):
            run('tar zxf monclient.tar.gz')
    elif app == 'supervisor':
        with lcd('../supervisor/'):
            put('monsupervisor.tar.gz', '/root/monsupervisor.tar.gz')
            run('tar zxf monsupervisor.tar.gz')
    elif app == 'webserver':
        with lcd('../webserver/'):
            put('monwebserver.tar.gz', '/root/monwebserver.tar.gz')
            run('tar zxf monwebserver.tar.gz')


def update_env(app):
    local('')
    pass


def launch(app):
    if app == 'clientroot':
        run('ls')
        with cd('/root/monkk/bin'):
            run('ls')
            run('./run_monclient.sh', pty=False)
    elif app == 'clientzhangnu':
        with cd('/home/zhangnu/monkk/bin'):
            run('./run_monclient.sh', pty=False)
    elif app == 'supervisor':
        with cd('/root/monsupervisor'):
            run('./run_monsupervisor.sh', pty=False)
    elif app == 'webserver':
        with cd('/root/monwebserver'):
            run('./run_webserver.sh', pty=False)

def afterrun(app):
    pass


def deploy(app):
    #set servers
    setservers(app)
    #local
    pack(app)
    #remote
    clean(app)
    upload(app)
    #update_env(app)
    launch(app)
    afterrun(app)

def install_pip_package(app):
    if app == 'client':
        with settings(warn_only=True):
            #install setuptools pip
            run('sudo apt-get update')
            run('sudo apt-get install -y python-setuptools')
            run('sudo apt-get install -y python-pip')
            #install package
            run('sudo pip install cron.py==0.0.5')

def removeoldclient():
    with settings(warn_only=True):
        run('rm -rf archive')
        run('cp -r monkk/archive ./archive')
        run('rm -rf monkk')
    run('mkdir monkk')
    with settings(warn_only=True):
        run('cp -r ./archive monkk/archive')
        run('rm -rf archive')

def test():
    run('ls')
    with cd('monkk'):
        run('ls')
    run('ls')
    #with settings(warn_only=True):
    #    run('cat /etc/issue')

def killclient():
    with settings(warn_only=True):
        run('ps aux | grep mon_client | grep python | awk \'{print $2}\' | xargs kill -9')
