# -*- encoding: utf-8 -*-

#proj   :py_toolkit
#module :daytime
#summary:used for compare two time, has nothing to do with date
#date   :Thu Oct 24 14:57:51 2013
#author :kk

from datetime import datetime
from datetime import timedelta

class DayTime(object):
    """used for compare two time, has nothing to do with date
    """
    def __init__(self, initime):
        if isinstance(initime, datetime):
            self.hour = initime.hour
            self.min = initime.minute
            self.sec = initime.second
        elif isinstance(initime, tuple):
            self.hour = initime[0]
            self.min = initime[1]
            self.sec = initime[2]
        else:
            raise TypeError

    def __le__(self,other): #x<=y calls x.__le__(y)
        if self.hour*3600 + self.min*60 + self.sec <= other.hour*3600 + other.min*60 + other.sec:
            return True
        return False

    def __ge__(self,other): #x>=y calls x.__ge__(y)
        return other.__le__(self)

    def __lt__(self,other): #x>y calls x.__gt__(y)
        if self.hour*3600 + self.min*60 + self.sec < other.hour*3600 + other.min*60 + other.sec:
            return True
        return False

    def __gt__(self,other): #x<y calls x.__lt__(y)
        return other.__lt__(self)

def yesterday():
    """return string like '20131025'
    """
    yesterday = datetime.now() - timedelta(days = 1)
    return yesterday.strftime('%Y%m%d')

if __name__ == '__main__':
    print yesterday()
    
