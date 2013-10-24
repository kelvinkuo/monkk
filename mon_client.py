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


import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import threading
import time
from datetime import date
import os
import re
import tarfile

WEB_SERVICE_PORT = 55666
WEB_ASSETS_ROOT = '/91logs/'
FLASHSERVER_ROOT = '/mg/'

class ThreadWebService(threading.Thread):
    """thread class,service as a web server"""
    def __init__(self):
        threading.Thread.__init__(self)

    def start_webservice(self):
        """launch a webservice for server to fectch log file """
        
        os.chdir(WEB_ASSETS_ROOT) #set the logs dir
        HandlerClass = SimpleHTTPRequestHandler
        ServerClass  = BaseHTTPServer.HTTPServer
        Protocol     = "HTTP/1.0"    
        server_address = ('0.0.0.0', WEB_SERVICE_PORT)
    
        HandlerClass.protocol_version = Protocol
        httpd = ServerClass(server_address, HandlerClass)
        
        sa = httpd.socket.getsockname()
        print "Serving HTTP on", sa[0], "port", sa[1], "..."
        httpd.serve_forever()

    def run(self):
        print 'ThreadWebService start running ...'
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
        print 'packing logs of last day...'
        yesterday = self.lastdate.strftime('%Y%m%d')
        tar = tarfile.open(os.path.join(WEB_ASSETS_ROOT,'flashserver_%s.tar.gz'%(yesterday)),'w:gz')
        for root,dirs,files in os.walk(os.path.join(FLASHSERVER_ROOT,'logs')):
            for file in files:
                if not re.match('^flashServer\.[0-9]+\.%s.+\.log'%(yesterday), file): continue
                tar.add(os.path.join(root,file))
        tar.close()
        
    def run(self):
        print 'ThreadPackage start running ...'
        while True:
            if self.diffday():
                self.packagelog()
                self.lastdate = date.today()
            time.sleep(30)

def init_check():
    if not os.path.exists(WEB_ASSETS_ROOT): #check logs dir
        os.makedirs(WEB_ASSETS_ROOT)

if __name__ == '__main__':
    
    init_check()

    th = ThreadPackage()
#    th.start()
    th.packagelog()

    quit()
    th = ThreadWebService()
    th.start()
