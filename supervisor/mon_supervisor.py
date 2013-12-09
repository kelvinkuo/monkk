#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

#proj   :monkk
#module :supervisor
#date   :2013-10-22


import os
import urllib
import logging
import logging.handlers
import tarfile
import re
import shutil
import util
import config
import time

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
        url = self.rex_url % (self.host, self.port, util.yesterday())
        try:
            if not os.path.exists(os.path.join(self.localdir, self.host)):
                os.makedirs(os.path.join(self.localdir, self.host))
            localfile = os.path.join(self.localdir, self.host, self.rex_localfile % util.yesterday())
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
    def __init__(self, workbench):
        self.workbench = workbench
        self.loghandlers = []

    def addloghandler(self, h):
        self.loghandlers.append(h)

    def prepare(self):
        raise NotImplementedError('prepare must be implemented')

    def getlogfilelist(self):
        raise NotImplementedError('getlogfilelist must be implemented')

    def do_parse(self):
        l = self.getlogfilelist()
        for h in self.loghandlers:
            h.dowork(l)

    def work(self):
        self.prepare()
        self.do_parse()


class TarLogParser(LogParser):
    def __init__(self, workbench, tarpath):
        LogParser.__init__(self, workbench)
        self.tarpath = tarpath

    def cleanworkbench(self):
        shutil.rmtree(self.workbench, ignore_errors=True)
        os.makedirs(self.workbench)

    def prepare(self):
        try:
            tar = tarfile.open(self.tarpath, 'r:gz')
            tar.extractall(self.workbench)
            tar.close()
        except tarfile.ReadError as e:
            print self.tarpath, e

    def getlogfilelist(self):
        l = []
        for root, dirs, files in os.walk(self.workbench):
            for f in files:
                l.append(os.path.join(root, f))

        return l

    def do_parse(self):
        LogParser.do_parse(self)
        self.cleanworkbench()


class YesterdayTarsLogParser(TarLogParser):
    def __init__(self, workbench, tarroot):
        TarLogParser.__init__(self, workbench, None)
        self.tarroot = tarroot

    def do_parse(self):
        l = self.getlogfilelist()
        for h in self.loghandlers:
            h.dowork(l, self.tarpath)
        self.cleanworkbench()

    def work(self):
        tarlist = []
        for root, dirs, files in os.walk(self.tarroot):
            for f in files:
                if re.search(util.yesterday(), f):
                    tarlist.append(os.path.join(root, f))
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

    def dowork(self, l, tarpath):
        for f in l:
            self.do_onefile(f, tarpath)

    def do_onefile(self, f, tarpath):
        raise NotImplementedError('do_onefile must be implemented')


class ClassPacketLostHandler(LogHandler):
    def __init__(self):
        LogHandler.__init__(self)

    def do_onefile(self, f, tarpath):
        if not os.path.exists(f):
            return

        if not re.match('.+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+.+\.tar\.gz', tarpath):
            return

        match = re.search('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', tarpath)
        serverip = tarpath[match.start(): match.end()]

        namecache = {}

        with open(f) as f:
            for line in f:
                if re.match('.+MONKK GC PacketLost.+', line):
                    res = re.split('[ ,=]', line)
#2013-11-19 17:28:58 MONKK GC PacketLost classid=43,userid=5,userdbid=20,stream=liveA3,count=0,toaddr=192.168.11.45:31585:3
#      0        1      2    3    4          5     6    7   8    9     10    11     12    13  14   15          16
                    if '' in res:
                        logging.error('none data: %s' % line)
                        continue
                    if res[14] == '0':  # count=0 not save
                        continue
                    if res[10] == '0':
                        continue
                    if '.' in res[6]:
                        res[6] = res[6].split('.')[0]
                    res[16] = res[16].split(':')[0]

                    dbid = res[10]
                    if dbid in namecache:
                        usrname = namecache[dbid]
                    else:
                        usrname = util.get_usrname(dbid)
                        namecache[dbid] = usrname
                        import time
                        time.sleep(2)

                    dbconn = util.getdbconn()
                    dbconn.execute(
                        "INSERT INTO t_gc_packetlost (classid,usrid,usrdbid,usrip,usrname,stream,recordtime,count,server) "
                        "VALUES (%s,%s,%s,'%s','%s','%s','%s %s',%s,'%s')"
                        % (res[6], res[8], res[10], res[16], usrname, res[12], res[0], res[1], res[14], serverip)
                    )

                elif re.match('.+MONKK GG PacketLost.+', line):
                    res = re.split('[ ,=]', line)
#2013-11-19 17:04:57 MONKK GG PacketLost classid=43.000,stream=liveA5,count=0,toaddr=192.168.11.45:31587:3
#      0        1      2    3    4          5     6        7      8     9   10   11       12
                    if '' in res:
                        logging.error('none data: %s' % line)
                        continue
                    if res[10] == '0':  # count=0 not save
                        continue
                    if '.' in res[6]:
                        res[6] = res[6].split('.')[0]
                    res[12] = res[12].split(':')[0]

                    dbconn = util.getdbconn()
                    dbconn.execute(
                        "INSERT INTO t_gg_packetlost (classid,mg_sour,mg_dest,stream,recordtime,count) "
                        "VALUES (%s,'%s','%s','%s','%s %s',%s)"
                        % (res[6], serverip, res[12], res[8], res[0], res[1], res[10])
                    )


class ClassDisConnHandler(LogHandler):
    def __init__(self):
        LogHandler.__init__(self)

    def do_onefile(self, f, tarpath):
        if not os.path.exists(f):
            return

        if not re.match('.+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+.+\.tar\.gz', tarpath):
            return

        match = re.search('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', tarpath)
        serverip = tarpath[match.start(): match.end()]

        namecache = {}
        dis_pre = []
        with open(f) as f:
            for line in f:
                if re.match('.+MONKK Disconnect state.+dbid.+', line):
                    res = re.split('[ ,=]', line)
#2013-11-27 11:47:50 MONKK Disconnect state=PrepareLeave,classid=5903,usrdbid=0,userid=0,toaddr=192.168.11.45:14456:3
#      0        1      2        3       4         5          6     7     8    9   10   11   12         13
                    if '' in res:
                        logging.error('none data: %s' % line)
                        continue
                    classid = res[7] if '.' not in res[7] else res[7].split('.')[0]
                    usrip = res[13].split(':')[0]
                    dbid = res[9]
                    usrid = res[11]
                    if dbid == '0':
                        continue

                    if dbid in namecache:
                        usrname = namecache[dbid]
                    else:
                        usrname = util.get_usrname(dbid)
                        namecache[dbid] = usrname
                        time.sleep(2)
                    recordtime = '%s %s' % (res[0], res[1])
                    state = res[5]

                    if state == 'PrepareLeave':
                        dis_pre.append(dbid)
                    elif state == 'CancelLeave':
                        if dbid in dis_pre:
                            dis_pre = filter(lambda a: a != dbid, dis_pre)

                elif re.match('.+MONKK RealDisconnect.+', line):
                    res = re.split('[ ,=]', line)
#2013-11-27 15:35:27 MONKK RealDisconnect classid=5903,usrdbid=0,userid=0,servertype=mcu,usrip=192.168.11.45:29062:3
#      0        1      2        3             4     5      6   7    8   9   10       11    12        13
                    if '' in res:
                        logging.error('none data: %s' % line)
                        continue
                    classid = res[5] if '.' not in res[5] else res[5].split('.')[0]
                    usrip = res[13].split(':')[0]
                    dbid = res[7]
                    usrid = res[9]
                    if dbid == '0':
                        continue

                    if dbid in namecache:
                        usrname = namecache[dbid]
                    else:
                        usrname = util.get_usrname(dbid)
                        namecache[dbid] = usrname
                        time.sleep(2)
                    recordtime = '%s %s' % (res[0], res[1])
                    servertype = res[11]

                    if dbid in dis_pre:
                        dis_pre = filter(lambda a: a != dbid, dis_pre)
                        continue

                    dbconn = util.getdbconn()
                    dbconn.execute(
                        "INSERT INTO t_disconnect (classid,usrdbid,usrid,usrip,usrname,servertype,serverip,recordtime) "
                        "VALUES (%s,%s,%s,'%s','%s','%s','%s','%s')"
                        % (classid, dbid, usrid, usrip, usrname, servertype, serverip, recordtime)
                    )


def supervisor():
    fetcher = LogFetcher()
    for ip in config.serverlist:
        fetcher.add_hosthandler(
            YesterdayDownloadHostHandler(
                ip, config.web_port,
                'http://%s:%s/archive/flashserver_%s.tar.gz',
                config.archivedir,
                'flashserver_%s.tar.gz'
            )
        )

    parser = YesterdayTarsLogParser(config.workbench, config.archivedir)
    h_lost = ClassPacketLostHandler()
    parser.addloghandler(h_lost)

    import cron
    cron_daemon = cron.Cron()
    cron_daemon.add('0 2 * * *', fetcher.fetchall)
    cron_daemon.add('0 3 * * *', parser.work)
    cron_daemon.start()
    cron_daemon.thread.join()


def testfetch():
    fetcher = LogFetcher()
    for ip in config.serverlist:
        fetcher.add_hosthandler(
            YesterdayDownloadHostHandler(
                ip, '55666',
                'http://%s:%s/archive/flashserver_%s.tar.gz',
                config.archivedir,
                'flashserver_%s.tar.gz'
            )
        )

    fetcher.fetchall()


def testparse():
    from lurker import connection
    conn = connection.Connection().quick_connect(
        'root',
        '91waijiao',
        dbname='91waijiao_mon_db',
        host='127.0.0.1'
    )
    parser = YesterdayTarsLogParser(config.workbench, config.archivedir, conn)
    h_lost = ClassPacketLostHandler()
    h_dis = ClassDisConnHandler()
    parser.addloghandler(h_lost)
    parser.addloghandler(h_dis)
    parser.work()


if __name__ == '__main__':
    util.init_log('mon_supervisor.%d.log' % os.getpid())
    supervisor()
    #testfetch()
    #testparse()
