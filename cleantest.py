# -*- encoding: utf-8 -*-

#proj   :mon
#module :clean tmp dir
#summary:clean tmp dir
#date   :Tue Oct 22 16:39:23 2013
#author :kk

import mon_client as config
import os

if __name__ == '__main__':
    print config.LOGS_DIR_PATH
    print config.SERVER_DIR_PATH

    os.removedirs(config.WEB_ASSETS_ROOT)
    os.removedirs(config.FLASHSERVER_ROOT)
