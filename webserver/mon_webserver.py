# -*- encoding: utf-8 -*-

#proj   :monkk
#module :web server
#date   :2013-11-21
#author :kk

import web
import config
import util

urls = (
  '/', 'index',
  '/login', 'login',
  '/logout', 'logout',
  '/classlost', 'classlost'
)

web.config.debug = False
app = web.application(urls, globals())

render = web.template.render(config.template_dir, globals={'hasattr': hasattr})
session = web.session.Session(app, web.session.DiskStore(config.session_dir))

######################
# Url Map Class
######################
class index(object):
    def GET(self):
        if session.get('loginned', False):
            print session.loginned
            return render.Tindex(1)
        else:
            param = web.input()
            if param.get('err', 'none') == 'passerr':
                return render.Tindex(2)
            return render.Tindex()


class login(object):
    def GET(self):
        raise web.seeother('/')

    def POST(self):
        param = web.input(return_url='/')
        if not hasattr(param, 'username') or not hasattr(param, 'password'):
            raise web.seeother('/')
        db = util.connect_db()
        check = db.query("SELECT * FROM t_account WHERE accname = '%s' and accpass = '%s'" % (param.username, param.password))
        if len(check) == 1:
            #web.setcookie('test', 'cookice_test', 60)
            session.loginned = True
            session.username = param.username
            raise web.seeother('/classlost')
        else:
            raise web.seeother('/?err=passerr')


class logout(object):
    def GET(self):
        session.loginned = False
        raise web.seeother('/')


class classlost(object):
    def GET(self):
        if not session.get('loginned', False):
            raise web.seeother('/')

        param = web.input()
        if not hasattr(param, 'classid'):
            return render.Tclslost(None)

        if not param.classid.isdigit():
            return render.Tclslost(None)

        db = util.connect_db()
        dbitems = db.query("SELECT * FROM t_gc_packetlost WHERE classid = %s ORDER BY usrdbid ASC, stream, recordtime" % param.classid)
        cl = ClassLostCollect(param.classid)
        cl.initgc(dbitems)
        dbitems = db.query("SELECT * FROM t_gg_packetlost WHERE classid = %s ORDER BY mg_sour ASC, recordtime" % param.classid)
        cl.initgg(dbitems)
        dbitems = db.query("SELECT * FROM t_disconnect WHERE classid = %s ORDER BY usrdbid ASC, recordtime" % param.classid)
        cl.initdis(dbitems)
        return render.Tclslost(cl)


######################
#
######################
class ClassLostCollect(object):
    """
    """
    def __init__(self, classid):
        self.classid = classid
        self._gcitems = []
        self._ggitems = []
        self._disitems = []

    def initgc(self, items):
        self._gcitems = items

    def initgg(self, items):
        self._ggitems = items

    def initdis(self, items):
        self._disitems = items

    def gcitems(self):
        for i in self._gcitems:
            yield i

    def ggitems(self):
        for i in self._ggitems:
            yield i

    def disitems(self):
        for i in self._disitems:
            yield i


if __name__ == "__main__":
    app.run()
