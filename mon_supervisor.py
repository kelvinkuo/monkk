#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

#proj   :monkk
#module :supervisor
#summary:中控服务，每天1点向client发送fetch请求，获取日志
#date   :Tue Oct 22 17:03:21 2013
#author :kk

#mon_supervisor only run under linux os

FLASHSERVER_LIST = ['192.241.207.26']
LOCAL_LOG_DIR = '/91_repos_logs/'

import time
from datetime import datetime
import threading
import urllib
import logging
import mon_client
from .. import daytime

class ThreadFetchLog(threading.Thread):
    """Thread Class for fetching log on every client
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.lastchecktime = DayTime(datetime.now())
        self.fetchtime = DayTime((1,0,0))
        
    def fetchlog(self):
        print 'fetch logs on all clients'
        yesterday = datetime.now()
        for server in FLASHSERVER_LIST:
            try:
                downloadurl = 'http://' + server + ':55666/flashserver_20131023.tar.gz'
                print 'downloading %s' % downloadurl
                urllib.urlretrieve(downloadurl, filename='/home/kk/flashserver_20131023.tar.gz')
            except Exception, e:               
                logging.warn('error downloading %s: %s' % (downloadurl, e))
        
    def run(self):
        print ' start running ...'
        while True:
            nowtime = DayTime(datetime.now())
            if nowtime >= self.fetchtime and self.lastchecktime <= self.fetchtime:
                self.fetchlog()
            self.lastchecktime = DayTime(datetime.now())
            time.sleep(30)

if __name__ == '__main__':
    
    th = ThreadFetchLog()
    th.fetchlog()
    th.fetchlog()
    quit()
    th.start()
