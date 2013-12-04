import web
import config
import urllib2
import logging

def connect_db():
    return web.database(**config.db_conf)

def get_usrname(dbid):
    try:
        response = urllib2.urlopen(config.api_getname % dbid, timeout=10)
    except urllib2.URLError, e:
        response = None
        logging.warn('fetch username error ddbid:%s' % dbid)
    return response.read() if response else ''
