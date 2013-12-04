from datetime import datetime
from datetime import timedelta

def yesterday():
    """return string like '20131025'
    """
    yesterday = datetime.now() - timedelta(days = 1)
    return yesterday.strftime('%Y%m%d')