# -*- encoding: utf-8 -*-

#import logging

debug = True

port = 8080

#data_dir = 'data/'

session_dir  = 'session/'

template_dir = 'templates/'
#template_cache = False

#need_log = True
#log_conf = {
#    'filename'  : 'web.log',
#    'level'     : logging.DEBUG,
#    'format'    : '[%(asctime)s] %(levelname)s: %(message)s',
#    'datefmt'   : '%Y-%m-%d %H:%M:%S',
#}

need_db = True
db_conf = {
    'dbn'  :'mysql',
    'db'   :'91waijiao_mon_db',
    'host' :'127.0.0.1',
    'user' :'root',
    'pw'   :'91waijiao'
}
#table = 'expense'

api_getname = 'http://api.91waijiao.com/app/get_user?uid=%s'