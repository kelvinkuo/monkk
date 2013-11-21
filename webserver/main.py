#proj   :monkk
#module :web
#summary:
#date   :2013-11-21
#author :kk

import web

urls = (
  '/', 'index',
  '/classlost', 'classlost'
)

render = web.template.render("templates/", globals={'hasattr':hasattr})
db = web.database(dbn='mysql', db='91waijiao_mon_db', host='192.168.11.47', user='root', pw='91waijiao')

######################
# Url Map Class
######################
class index(object):
    def GET(self):
        return "91waijiao monitoting system"


class classlost(object):
    def GET(self):
        param = web.input()
        if not hasattr(param, 'classid'):
            return render.classlost(None)

        dbitems = db.query("SELECT * FROM t_gc_packetlost WHERE classid = %s ORDER BY recordtime ASC" % param.classid)
        cl = ClassLostCollect().initfromquery(dbitems)
        return render.classlost(cl)

######################
#
######################
class ClassLostCollect(object):
    def __init__(self):
        self.classid = None
        self.usrs = []

    def initfromquery(self, items):
        for item in items:
            #find ClassUser obj
            #find Stream obj
            #add item to Stream
        pass

    def users(self):
        for usr in self.usrs:
            yield usr

class ClassUser(object):
    def __init__(self):
        pass

    def dbid(self):
        pass

    def usrid(self):
        pass

    def streams(self):
        pass

class Stream(object):
    def __init__(self):
        pass

    def name(self):
        pass

    def items(self):
        pass

class LostItem(object):
    def __init__(self):
        pass


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
