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

import sys,os,time,threading,urllib,logging,logging.handlers,tarfile,re
from datetime import datetime
from daytime import DayTime
from daytime import yesterday

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
            except Exception(e):               
                logging.error('downloading %s: %s', downloadurl, e)
        
    def run(self):
        logging.info('ThreadFetchLog start running')
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
        
        l=[]
        for root,dirs,files in os.walk(LOG_CLASS_DIR):
            for file in files:
                l.append(os.path.join(root,file))

        # parse
        self.parseclasspacketlost(l)
        # clean files
        for i in l:
            try:
                os.remove(i)
            except:
                logging.error('parselog cant remove %s', i)
    
    def getclasslist(self,flist):
        set_class = set()
        for f in flist:
            file = open(f,'r')
            for line in file:
                if 'MONKK PacketLost' not in line: continue
                set_class.add(re.split('[ =,\.]', line)[5])
            file.close()
            
        return list(set_class)

    def parseclasspacketlost(self,flist):
        classlist = self.getclasslist(flist)
        for f in flist:
            file = open(f,'r')
            for line in file:
                if 'MONKK PacketLost' not in line: continue
                
                
            file.close()

    def run(self):
        logging.info('ThreadParseLog start running')
        while True:
            nowtime = DayTime(datetime.now())
            if nowtime > self.parsetime and self.lastchecktime <= self.parsetime:
                self.parselog()
            self.lastchecktime = DayTime(datetime.now())
            time.sleep(30)

# def grep(pattern,word_list):
#     expr = re.compile(pattern)
#     return [elem for elem in word_list if expr.match(elem)]

def init_log(fname):
    """init the log module, use the root logger
    """
    formatter = logging.Formatter('%(asctime)s %(message)s(%(levelname)s)(%(threadName)s)','%Y%m%d_%H:%M:%S')
    fh = logging.FileHandler(fname)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    mh = logging.handlers.MemoryHandler(10,target=fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    
    logging.getLogger().addHandler(mh)
    logging.getLogger().addHandler(ch)
    
    logging.getLogger().setLevel(logging.DEBUG)

    logging.info('completed: init_log logfile=%s' % (fname))

if __name__ == '__main__':
    init_log('mon_supervisor.%d.log'%(os.getpid()))
    
    logging.info("1")
    logging.info("2")
    logging.info("3")
    logging.info("4")
    logging.info("5")
    time.sleep(20)
    
#    l = ThreadParseLog().getclasslist(['flashServer.4624.20131016_154628.mg-0.log'])
#    print l
    
#    print re.split('[ =,\.]', '2013-10-16 16:44:22 MONKK PacketLost classid=5904,userid=0,count=0')[5]
    quit()
    # for i in range(5):
    #     logging.info('yo yo check now')
    #     logging.warning('warning')
    #     logging.error('error come')
    # quit()
    th = ThreadParseLog()
    th.start()
#    th.parselog(yesterday())

    th = ThreadFetchLog()
    th.start()