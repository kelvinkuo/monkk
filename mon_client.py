#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

#proj   :monkk
#module :client
#summary:部署在被监控服务器上，负责日志打包和响应日志获取请求
#date   :Tue Oct 22 10:49:11 2013
#author :kk

#使用root用户运行
#每天凌晨 定时打包前一日日志
#等待中控服务器的fetch请求


import sys,time,threading,os,re,tarfile,logging,logging.handlers,shutil
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from datetime import date

WEB_SERVICE_PORT = 55666
WEB_ASSETS_ROOT = './archive'
LOG_ARCHIVE_DIR = './91logs/'
if 'win' in sys.platform:
    FLASHSERVER_ROOT = 'D:/91flash_release_20131029'
else:
    FLASHSERVER_ROOT = '/mg/release_20131105/server/'

class ThreadWebService(threading.Thread):
    """thread class,service as a web server
    """
    def __init__(self):
        threading.Thread.__init__(self)

    def start_webservice(self):
        """launch a webservice for server to fectch log file
        """
        #os.chdir(WEB_ASSETS_ROOT) #set the logs dir
        HandlerClass = SimpleHTTPRequestHandler
        ServerClass  = BaseHTTPServer.HTTPServer
        Protocol     = "HTTP/1.0"    
        server_address = ('0.0.0.0', WEB_SERVICE_PORT)
    
        HandlerClass.protocol_version = Protocol
        httpd = ServerClass(server_address, HandlerClass)
        
        sa = httpd.socket.getsockname()
        logging.info("Serving HTTP on %s:%d" % (sa[0], sa[1]))
        httpd.serve_forever()

    def run(self):
        logging.info('ThreadWebService start running ...')
        self.start_webservice()

class ThreadPackage(threading.Thread):
    """Thread Class for packing logs to tar file
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.lastdate = date.today()

    def diffday(self):
        _diffdate = date.today() - self.lastdate
        if _diffdate.days > 0:
            return True
        else:
            return False

    def packagelog(self):
        yesterday = self.lastdate.strftime('%Y%m%d')
        logging.info('start packing logs, date:%s' %(yesterday))
        archivefile = 'flashserver_%s.tar.gz'%(yesterday)
        tar = tarfile.open(os.path.join(LOG_ARCHIVE_DIR,archivefile),'w:gz')
        for root,dirs,files in os.walk(os.path.join(FLASHSERVER_ROOT,'logs')):
            for file in files:
                if not re.match('^flashServer\.[0-9]+\.%s.+\.log'%(yesterday), file): continue
                shutil.copyfile(os.path.join(root,file), os.path.join(LOG_ARCHIVE_DIR,file))
                tar.add(os.path.join(LOG_ARCHIVE_DIR,file) ,recursive=False)
                logging.info()
                os.remove(os.path.join(LOG_ARCHIVE_DIR,file))
        tar.close()
        shutil.move(os.path.join(LOG_ARCHIVE_DIR,archivefile), os.path.join(WEB_ASSETS_ROOT,archivefile))
        
    def run(self):
        logging.info('ThreadPackage start running ...')
        while True:
            if self.diffday():
                self.packagelog()
                self.lastdate = date.today()
            time.sleep(30)

def init_log(fname):
    """init the log module, use the root logger
    """
    formatter = logging.Formatter('%(asctime)s %(message)s(%(levelname)s)(%(threadName)s)','%Y%m%d_%H:%M:%S')

    fh = logging.FileHandler(fname)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
#    mh = logging.handlers.MemoryHandler(10,target=fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    
#    logging.getLogger().addHandler(mh)
    logging.getLogger().addHandler(fh)
    logging.getLogger().addHandler(ch)
    
    logging.getLogger().setLevel(logging.DEBUG)

    logging.info('logfile:%s' % (fname))

def init_check():
    if not os.path.exists(LOG_ARCHIVE_DIR):
        os.makedirs(LOG_ARCHIVE_DIR)
    if not os.path.exists(WEB_ASSETS_ROOT):
        os.makedirs(WEB_ASSETS_ROOT)

if __name__ == '__main__':
    init_log('mon_client.%d.log'%(os.getpid())) #log must be the first module to be launched
    init_check()

    th = ThreadPackage()
    th.start()

    th = ThreadWebService()
    th.start()
