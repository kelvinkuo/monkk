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


import sys, time, threading, os, re, tarfile, logging, logging.handlers, daytime
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from datetime import date

WEB_SERVICE_PORT = 55666
WEB_ASSETS_ROOT = './archive'
if 'win' in sys.platform:
    FLASHSERVER_ROOT = 'D:/'
else:
    FLASHSERVER_ROOT = '/mg/'


class ThreadWebService(threading.Thread):
    """thread class,service as a web server
    """
    def __init__(self):
        threading.Thread.__init__(self)

    def start_webservice(self):
        """launch a webservice for server to fectch log file
        """
        handlerclass = SimpleHTTPRequestHandler
        serverclass = BaseHTTPServer.HTTPServer
        protocol = "HTTP/1.0"
        server_address = ('0.0.0.0', WEB_SERVICE_PORT)
    
        handlerclass.protocol_version = protocol
        httpd = serverclass(server_address, handlerclass)
        
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
        self.interval = 30
        self.path_handler = []
        self.file_handler = []

    def add_pathhandler(self, h):
        self.path_handler.append(h)

    def add_filehandler(self, h):
        self.file_handler.append(h)

    def set_interval(self, secs):
        self.interval = secs

    def packagelog(self):
        logging.info('start packing logs of yesterday')

        for ph in self.path_handler:
            l = ph.get_files()
            for fh in self.file_handler:
                fh.dofiles(l)

    def diffday(self):
        _diffdate = date.today() - self.lastdate
        if _diffdate.days > 0:
            return True
        else:
            return False

    def run(self):
        logging.info('ThreadPackage start running ...')
        while True:
            if self.diffday():
                self.packagelog()
                self.lastdate = date.today()
            time.sleep(self.interval)


###########################################
#PathHandler
###########################################
class PathHandler(object):
    def __init__(self, root, rex_dir, rex_file):
        self.root = root
        self.rex_dir = rex_dir
        self.rex_file = rex_file

    def get_files(self):
        l = []
        for root, dirs, files in os.walk(self.root):
            if not re.search(self.rex_dir, root):
                continue
            for f in files:
                if not re.match(self.rex_file, f):
                    continue
                l.append(os.path.join(root, f))
        return l


class YesterdayPathHandler(PathHandler):
    def __init__(self, root, rex_dir, rex_file_pattern):
        PathHandler.__init__(self, root, rex_dir, None)
        self.rex_file_pattern = rex_file_pattern

    def get_files(self):
        self.rex_file = self.rex_file_pattern.replace('%s', daytime.yesterday())
        return PathHandler.get_files(self)


###########################################
#FilesHandler
###########################################
class FilesHandler(object):
    def __init__(self):
        pass

    def dofiles(self, l):
        raise NotImplementedError('dofiles must be implemented')


class TarFilesHandler(FilesHandler):
    def __init__(self, tarpath):
        FilesHandler.__init__(self)
        self.tarpath = tarpath

    def dofiles(self, l):
        try:
            tar = tarfile.open(self.tarpath, 'w:gz')
            logging.info('create tarfile %s' % self.tarpath)
            for fpath in l:
                tar.add(fpath)
                logging.info('add log to tarfile : %s' % fpath)
            tar.close()
        except BaseException as e:
            logging.error('TarFilesHandler dofiles msg: %s' % e.message)


class YesterdayTarFilesHandler(TarFilesHandler):
    def __init__(self, tarpath_pattern):
        TarFilesHandler.__init__(self, None)
        self.tarpath_pattern = tarpath_pattern

    def dofiles(self, l):
        self.tarpath = self.tarpath_pattern.replace('%s', daytime.yesterday())
        TarFilesHandler.dofiles(self, l)


class CleanFilesHandler(FilesHandler):
    def __init__(self):
        FilesHandler.__init__(self)

    def dofiles(self, l):
        for fpath in l:
            try:
                os.remove(fpath)
            except IOError:
                logging.error('CleanFilesHandler cant remove %s' % fpath)


def init_log(fname):
    """init the log module, use the root logger
    """
    formatter = logging.Formatter('%(asctime)s %(message)s(%(levelname)s)(%(threadName)s)', '%Y%m%d_%H:%M:%S')

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

    logging.info('logfile:%s' % fname)


def init_check():
    if not os.path.exists(WEB_ASSETS_ROOT):
        os.makedirs(WEB_ASSETS_ROOT)

if __name__ == '__main__':
    init_log('mon_client.%d.log' % os.getpid())  # log must be the first module to be launched
    init_check()

    th = ThreadPackage()
    if 'win' in sys.platform:
        ph = YesterdayPathHandler(FLASHSERVER_ROOT, '91flash_release_[0-9]+.logs', '^flashServer\.[0-9]+\.%s.+\.log')
    else:
        ph = YesterdayPathHandler(FLASHSERVER_ROOT, 'release_[0-9]+.server.logs', '^((mg)|(flashServer))\.[0-9]+\.%s.+\.log')
    th.add_pathhandler(ph)
    fh = YesterdayTarFilesHandler(os.path.join(WEB_ASSETS_ROOT, 'flashserver_%s.tar.gz'))
    th.add_filehandler(fh)
    th.set_interval(10)
    th.start()

    ThreadWebService().start()

    #from datetime import datetime
    #from datetime import timedelta
    #for i in range(1,9):
    #    day = (datetime.now() - timedelta(days = i)).strftime('%Y%m%d')
    #    th = ThreadPackage()
    #    if 'win' in sys.platform:
    #        th.add_pathhandler(PathHandler(FLASHSERVER_ROOT, '91flash_release_[0-9]+.logs', '^flashServer\.[0-9]+\.%s.+\.log' % day))
    #    else:
    #        th.add_pathhandler(PathHandler(FLASHSERVER_ROOT, 'release_[0-9]+.server.logs', '^((mg)|(flashServer))\.[0-9]+\.%s.+\.log' % day))
    #    th.add_pathhandler(PathHandler(FLASHSERVER_ROOT, '91flash_release_[0-9]+.logs', '^flashServer\.[0-9]+\.%s.+\.log' % day))
    #    th.add_filehandler(TarFilesHandler(os.path.join(WEB_ASSETS_ROOT, 'flashserver_%s.tar.gz' % day)))
    #    th.packagelog()