#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

#proj   :monkk
#module :supervisor
#summary:中控服务，每天1点向client发送fetch请求，获取日志
#date   :Tue Oct 22 17:03:21 2013
#author :kk

#mon_supervisor only run under linux os

FLASHSERVER_LIST = [
#windows
'42.121.34.105',
'58.68.229.42',
'98.126.132.210',
'203.90.245.15',
#linux
'192.241.207.26',
'106.186.116.170',
'14.18.206.3',
'110.34.240.58',
'70.39.189.80',
'42.121.76.137'
]

ARCHIVE_DIR = './archive_logs/'
WORKBENCH = './workbench/'
#THREAD_REDIS_CLIENT_NUM = 5

import sys,os,time,threading,urllib,logging,logging.handlers,tarfile,re,redis
from datetime import datetime
from Queue import Queue

from daytime import DayTime
from daytime import yesterday

###########################################
#fectch module
###########################################
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
            downloadurl = 'http://%s:55666/archive/flashserver_%s.tar.gz' % (server, yest)
            try:
                logging.info('downloading %s', downloadurl)
                if not os.path.exists(os.path.join(ARCHIVE_DIR, server)): os.makedirs(os.path.join(ARCHIVE_DIR, server))
                urllib.urlretrieve(downloadurl, filename=os.path.join(ARCHIVE_DIR, 'flashserver_%s.tar.gz' % (yest)))
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

###########################################
#parse module
###########################################
class ThreadParseLog(threading.Thread):
    """
    """
    def __init__(self,handlers=None):
        threading.Thread.__init__(self)
        self.lastchecktime = DayTime(datetime.now())
        self.parsetime = DayTime((3,0,0)) #03:00:00
        #self.curworkdir = None
        #self.que_redis = q
        self.handlers = handlers

    def parse_date(self,date):
        for root,dirs,files in os.walk(ARCHIVE_DIR):
            for file in files:
                if not re.match('^flashServer\.[0-9]+\.%s.+\.log'%(date), file): continue
                self.parse_tarfile(os.path.join(root,file))

    def parse_tarfile(self,file):
        tar = tarfile.open(file,'r:gz')
        tar.extractall(WORKBENCH)
        tar.close()
        
        l=[]
        for root,dirs,files in os.walk(WORKBENCH):
            for file in files:
                l.append(os.path.join(root,file))

        if self.handlers is not None:
            for h in self.handlers:
                h.dowork(l)

        for f in l:
            try: os.remove(f)
            except: logging.error('parse_tarfile cant remove %s', f)
    
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
                #self.que_redis.put({})
                
            file.close()

    def run(self):
        logging.info('ThreadParseLog start running')
        while True:
            nowtime = DayTime(datetime.now())
            if nowtime > self.parsetime and self.lastchecktime <= self.parsetime:
                self.parse_date(yesterday())
            self.lastchecktime = DayTime(datetime.now())
            time.sleep(30)

class LogHandler(object):
    def __init__(self,handlers=None):
        self.handlers = handlers

    def dowork(self,l):
        for f in l:
            self.do_onefile(f)

    def do_onefile(self,f):
        raise NotImplementedError('do_onefile must be implemented')

class ClassPacketLostHandler(LogHandler):
    def __init__(self,handlers=None):
        LogHandler.__init__(self,handlers)

    def do_onefile(self,f):
        #todo
        pass

class ClassDisConnHandler(LogHandler):
    def __init__(self,handlers=None):
        LogHandler.__init__(self,handlers)

    def do_onefile(self,f):
        #todo
        pass

class SaveHandler(object):
    def __init__(self):
        pass

    def StrSet(self, key, value):
        raise NotImplementedError('StrSet must be implemented')

    def StrGet(self, key):
        raise NotImplementedError('Strget must be implemented')

class RedisSaveHandler(SaveHandler):
    def __init__(self):
        SaveHandler.__init__(self)

    def StrSet(self, key, value):

        pass

    def StrGet(self, key):
        #todo
        pass
#class ThreadRedis(threading.Thread):
#
#    def __init__(self,q):
#        threading.Thread.__init__(self)
#        self.q = q
#        #connect redis server
#
#    def savedata(self,item):
#
#        pass
#
#    def run(self):
#        while True:
#            item = self.q.get()
#            self.savedata(item)
#            self.q.task_done()


def init_log(fname):
    """init the log module, use the root logger
    """
    formatter = logging.Formatter('%(asctime)s %(message)s(%(levelname)s)(%(threadName)s)','%Y%m%d_%H:%M:%S')

    fh = logging.FileHandler(fname)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    #mh = logging.handlers.MemoryHandler(10,target=fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    
    #logging.getLogger().addHandler(mh)
    logging.getLogger().addHandler(fh)
    logging.getLogger().addHandler(ch)
    
    logging.getLogger().setLevel(logging.DEBUG)

    logging.info('logfile:%s' % (fname))

if __name__ == '__main__':
    
    init_log('mon_supervisor.%d.log'%(os.getpid())) #log must be the first module to be launched
    
    #que_redis_save = Queue() #saving log data to redis queue

    #for i in range(THREAD_REDIS_CLIENT_NUM):
    #    ThreadRedis(que_redis_save).start()
    #
    #import random
    #for i in range(100000):
    #    logging.info('for %d' % i)
    #    que_redis_save.put(('V',random.randint(0,270),'192.168.11.45'))
    
    #quit()
    #ThreadParseLog(que_redis_save).start()
#    th.parse_tarfile(yesterday())

    th = ThreadFetchLog()
    th.start()

    redisHandler = RedisSaveHandler()
    th = ThreadParseLog( [ClassDisConnHandler([redisHandler]),
                          ClassPacketLostHandler([redisHandler])] )
    th.start()
