from datetime import datetime
from datetime import timedelta
import urllib2
import config
import logging
import sys


def yesterday():
    """return string like '20131025'
    """
    yesterday = datetime.now() - timedelta(days = 1)
    return yesterday.strftime('%Y%m%d')


def get_usrname(dbid):
    try:
        response = urllib2.urlopen(config.api_getname % dbid, timeout=10)
    except urllib2.URLError, e:
        response = None
        logging.warn('fetch username error ddbid:%s' % dbid)
    return response.read() if response else ''


def init_log(fname):
    """init the log module, use the root logger
    """
    formatter = logging.Formatter('%(asctime)s %(message)s(%(levelname)s)(%(threadName)s)', '%Y%m%d_%H:%M:%S')

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

    logging.info('logfile:%s' % fname)

def getdbconn():
    from lurker import connection
    conn = connection.Connection().quick_connect(
        config.dbuser,
        config.dbpasswd,
        dbname=config.dbname,
        host=config.dbhost
    )
    return conn
