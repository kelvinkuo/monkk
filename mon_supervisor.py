#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

#proj   :monkk
#module :supervisor
#summary:中控服务，每天1点向client发送fetch请求，获取日志
#date   :Tue Oct 22 17:03:21 2013
#author :kk

#mon_supervisor only run under linux os

FLASHSERVER_LIST = ['192.241.207.26']
LOCAL_LOG_DIR = '/91_flashserver_logs/bak/'
LOG_CLASS_DIR = '/91_flashserver_logs/class/'

import os,time,threading,urllib,logging,tarfile
from datetime import datetime
from daytime import DayTime
from daytime import yesterday

logging.basicConfig(format='%(asctime)s %(message)s',
                    filename='mon_supervisor.log',
                    datefmt='%Y%m%d_%H:%M:%S',
                    level=logging.DEBUG)

class ThreadFetchLog(threading.Thread):
    """Thread Class for fetching log on every client
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.lastchecktime = DayTime(datetime.now())
        self.fetchtime = DayTime((1,0,0))
        
    def fetchlog(self):
        logging.info('fetch logs on all clients')
        yest = yesterday()
        for server in FLASHSERVER_LIST:
            try:
                downloadurl = 'http://%s:55666/flashserver_%s.tar.gz' % (server, yest)
                logging.info('downloading %s', downloadurl)
                urllib.urlretrieve(downloadurl, filename = os.path.join(LOCAL_LOG_DIR, 'flashserver_%s.tar.gz' % (yest)))
            except Exception, e:               
                logging.warn('error downloading %s: %s', downloadurl, e)
        
    def run(self):
        logging.info('ThreadFetchLog start running ...')
        while True:
            nowtime = DayTime(datetime.now())
            if nowtime > self.fetchtime and self.lastchecktime <= self.fetchtime:
                self.fetchlog()
            self.lastchecktime = DayTime(datetime.now())
            time.sleep(30)

class ThreadParseLog(threading.Thread):
    """
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.lastchecktime = DayTime(datetime.now())
        self.parsetime = DayTime((3,0,0)) #03:00:00
        self.curworkdir = None

    def parselog(self,logdate):
        # unpack tar file
        tar = tarfile.open(os.path.join(LOCAL_LOG_DIR,'flashserver_%s.tar.gz'%(logdate)),'r:gz')
        tar.extractall(LOG_CLASS_DIR)
        tar.close()
        # parse
        self.parsebyclass()
        # clean files
        for root,dirs,files in os.walk(LOG_CLASS_DIR):
            for file in files:
                try:
                    os.remove(os.path.join(root,file))
                except:
                    logging.warning('can\'t remove %s', os.path.join(root,file))


    def parsebyclass(self):
        if self.curworkdir is None: return
        

    def run(self):
        logging.info('ThreadParseLog start running')
        while True:
            nowtime = DayTime(datetime.now())
            if nowtime > self.parsetime and self.lastchecktime <= self.parsetime:
                self.parselog()
            self.lastchecktime = DayTime(datetime.now())
            time.sleep(30)

def grep(pattern,word_list):
    expr = re.compile(pattern)
    return [elem for elem in word_list if expr.match(elem)]

if __name__ == '__main__':
    

    logging.info('yo yo check now')
    logging.warning('warning')
    quit()
    th = ThreadParseLog()
    th.parselog(yesterday())
    quit()

    
    th = ThreadFetchLog()
    th.start()
