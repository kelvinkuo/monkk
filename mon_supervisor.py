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

import sys,os,time,threading,urllib,logging,logging.handlers,tarfile,re,redis,croniter
from datetime import datetime
from Queue import Queue

from daytime import DayTime
from daytime import yesterday

###########################################
#fectch module
###########################################
#class ThreadFetchLog(threading.Thread):
#    """Thread Class for fetching log on every client
#    """
#    def __init__(self):
#        threading.Thread.__init__(self)
#        self.lastchecktime = DayTime(datetime.now())
#        self.fetchtime = DayTime((1,0,0))
#
#    def fetchlog(self):
#        logging.info('fetch logs on all clients')
#        yest = yesterday()
#        for server in FLASHSERVER_LIST:
#            downloadurl = 'http://%s:55666/archive/flashserver_%s.tar.gz' % (server, yest)
#            try:
#                logging.info('downloading %s', downloadurl)
#                if not os.path.exists(os.path.join(ARCHIVE_DIR, server)): os.makedirs(os.path.join(ARCHIVE_DIR, server))
#                urllib.urlretrieve(downloadurl, filename=os.path.join(ARCHIVE_DIR, 'flashserver_%s.tar.gz' % (yest)))
#            except Exception(e):
#                logging.error('downloading %s: %s', downloadurl, e)
#
#    def run(self):
#        logging.info('ThreadFetchLog start running')
#        while True:
#            nowtime = DayTime(datetime.now())
#            if nowtime > self.fetchtime >= self.lastchecktime:
#                self.fetchlog()
#            self.lastchecktime = DayTime(datetime.now())
#            time.sleep(30)

class TimerThread(threading.Thread):
    """

    """
    def __init__(self, time_pattern, task):
        threading.Thread.__init__(self)
        self.time_pattern = time_pattern
        self.task = task

    @classmethod
    def checktime(cls, now, time_pattern):
        #todo
        pass

    def run(self):
        while True:
            if TimerThread.checktime(datetime.now(), self.time_pattern):
                self.task()


###########################################
#Controler
#drive the host handler to fetch logs
###########################################
class LogFetcher(object):
    """fetch logs compressed in tarfile"""
    def __init__(self):
        self.hosthandlers = []

    def add_hosthandler(self, hh):
        self.hosthandlers.append(hh)

    def fetchall(self):
        l = []
        for hh in self.hosthandlers:
            fl = hh.handlehost()
            if fl is not None:
                l.append(fl)

        return l

###########################################
#HostHandler
#download file from some host
###########################################
class HostHandler(object):
    def __init__(self, host):
        self.host = host

    def handlehost(self):
        raise NotImplementedError('handlehost must be implemented')


class YesterdayDownloadHostHandler(HostHandler):
    def __init__(self, host, port, rex_url, localdir, rex_localfile):
        HostHandler.__init__(self, host)
        self.port = port
        self.rex_url = rex_url
        self.localdir = localdir
        self.rex_localfile = rex_localfile

    def handlehost(self):
        #url = self.rex_url
        url = self.rex_url % (self.host, self.port, yesterday())
        try:
            if not os.path.exists(os.path.join(self.localdir, self.host)):
                os.makedirs(os.path.join(self.localdir, self.host))
            localfile = os.path.join(self.localdir, self.host, self.rex_localfile % yesterday())
            urllib.urlretrieve(url, filename=localfile)
            logging.info('downloaded ok %s', url)
            return localfile
        except Exception as e:
            logging.error('downloaded error %s: %s', url, e)


###########################################
#Controler
#drive loghandler to parse log file
###########################################
class LogParser(object):
    def __init__(self, workbench, conn):
        self.workbench = workbench
        self.loghandlers = []
        self.dbconn = conn

    def addloghandler(self, h):
        self.loghandlers.append(h)

    def prepare(self):
        raise NotImplementedError('prepare must be implemented')

    def getlogfilelist(self):
        raise NotImplementedError('getlogfilelist must be implemented')

    def do_parse(self):
        l = self.getlogfilelist()
        for h in self.loghandlers:
            h.dowork(l, self.dbconn)

    def work(self):
        self.prepare()
        self.do_parse()


class TarLogParser(LogParser):
    def __init__(self, workbench, tarpath):
        LogParser.__init__(self, workbench)
        self.tarpath = tarpath

    def cleanworkbench(self):
        for root,dirs,files in os.walk(self.workbench):
            for file in files:
                try:
                    os.remove(file)
                except BaseException as e:
                    continue

    def prepare(self):
        tar = tarfile.open(self.tarpath, 'r:gz')
        tar.extractall(self.workbench)
        tar.close()

    def getlogfilelist(self):
        l = []
        for root,dirs,files in os.walk(self.workbench):
            for file in files:
                l.append(os.path.join(root,file))

    def do_parse(self):
        LogParser.do_parse(self)
        self.cleanworkbench()

class YesterdayTarsLogParser(TarLogParser):
    def __init__(self, workbench, tarroot):
        TarLogParser.__init__(self, workbench, None)
        self.tarroot = tarroot

    def work(self):
        tarlist = []
        for root,dirs,files in os.walk(self.tarroot):
            for file in files:
                if re.search(yesterday(), file):
                    tarlist.append(os.path.join(root,file))
        for tar in tarlist:
            self.tarpath = tar
            TarLogParser.work(self)

        self.tarpath = None

###########################################
#Log Handler
#input:file list
###########################################
class LogHandler(object):
    def __init__(self):
        pass

    def dowork(self, l, dbconn):
        for f in l:
            self.do_onefile(f, dbconn)

    def do_onefile(self, f, dbconn):
        raise NotImplementedError('do_onefile must be implemented')


class ClassPacketLostHandler(LogHandler):
    def __init__(self):
        LogHandler.__init__(self)

    def do_onefile(self, f, dbconn):
        if not os.path.exists(f):
            return
        file = open(f)
        for line in file:
            if re.match('.+MONKK PacketLost.+', line):
                #dbconn.save
                print line
                #print 'dbconn save %s'
        file.close()


#class ClassDisConnHandler(LogHandler):
#    def __init__(self):
#        LogHandler.__init__(self)
#
#    def do_onefile(self,f):
#        pass
############################################
##Save Handler
##input:save request
############################################
#class SaveHandler(object):
#    def __init__(self):
#        pass
#
#    def save(self, data):
#        oper = data[0]
#        if oper == 'strset':
#            self.strset(data[1], data[2])
#        elif oper == 'strget':
#            return self.strget(data[1])
#        else:
#            return
#
#    def strset(self, key, value):
#        raise NotImplementedError('strset must be implemented')
#
#    def strget(self, key):
#        raise NotImplementedError('strget must be implemented')
#
#
#class RedisSaveHandler(SaveHandler):
#    def __init__(self):
#        SaveHandler.__init__(self)
#
#    def strset(self, key, value):
#        pass
#
#    def strget(self, key):
#        pass
###########################################
#parse module
###########################################
#class ThreadParseLog(threading.Thread):
#    """
#    """
#    def __init__(self,handlers=None):
#        threading.Thread.__init__(self)
#        self.lastchecktime = DayTime(datetime.now())
#        self.parsetime = DayTime((3,0,0)) #03:00:00
#        #self.curworkdir = None
#        #self.que_redis = q
#        self.handlers = handlers
#
#    def parse_date(self,date):
#        for root,dirs,files in os.walk(ARCHIVE_DIR):
#            for file in files:
#                if not re.match('^flashServer\.[0-9]+\.%s.+\.log'%(date), file): continue
#                self.parse_tarfile(os.path.join(root,file))
#
#    def parse_tarfile(self,file):
#        tar = tarfile.open(file,'r:gz')
#        tar.extractall(WORKBENCH)
#        tar.close()
#
#        l=[]
#        for root,dirs,files in os.walk(WORKBENCH):
#            for file in files:
#                l.append(os.path.join(root,file))
#
#        if self.handlers is not None:
#            for h in self.handlers:
#                h.dowork(l)
#
#        for f in l:
#            try: os.remove(f)
#            except: logging.error('parse_tarfile cant remove %s', f)
#
#    def getclasslist(self,flist):
#        set_class = set()
#        for f in flist:
#            file = open(f,'r')
#            for line in file:
#                if 'MONKK PacketLost' not in line: continue
#                set_class.add(re.split('[ =,\.]', line)[5])
#            file.close()
#
#        return list(set_class)
#
#    def parseclasspacketlost(self,flist):
#        classlist = self.getclasslist(flist)
#        for f in flist:
#            file = open(f,'r')
#            for line in file:
#                if 'MONKK PacketLost' not in line: continue
#                #self.que_redis.put({})
#
#            file.close()
#
#    def run(self):
#        logging.info('ThreadParseLog start running')
#        while True:
#            nowtime = DayTime(datetime.now())
#            if nowtime > self.parsetime >= self.lastchecktime:
#                self.parse_date(yesterday())
#            self.lastchecktime = DayTime(datetime.now())
#            time.sleep(30)

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
    
    init_log('mon_supervisor.%d.log' % os.getpid()) #log must be the first module to be launched

    fetcher = LogFetcher()
    for ip in FLASHSERVER_LIST:
        fetcher.add_hosthandler(YesterdayDownloadHostHandler(ip, '55666',
                                                         'http://%s:%s/archive/flashserver_%s.tar.gz',
                                                         ARCHIVE_DIR,
                                                         'flashserver_%s.tar.gz'))
    tars = fetcher.fetchall()


    h_lost = ClassPacketLostHandler()
    parser = YesterdayTarsLogParser(WORKBENCH, ARCHIVE_DIR)
    parser.addloghandler(h_lost)
    parser.work()