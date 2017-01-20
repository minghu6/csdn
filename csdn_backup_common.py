# -*- coding:utf-8 -*-
#!/usr/bin/env python3

"""

"""
import datetime
from collections  import namedtuple
import os

from minghu6.etc.datetime import datetime_fromstr

EssayBrief  = namedtuple('EssayBrief', ['id', 'datetime'])

def write_blog_backup_log(d:datetime.datetime=datetime.datetime.now()):
    with open('.csdn_blog_log') as fw:
        fw.write(d.__str__())


def read_blog_backup_log():
    if not os.path.exists('.csdn_blog_log'):
        d = datetime.datetime.fromtimestamp(0)
    else:
        with open('.csdn_blog_log') as fr:
            d = datetime_fromstr(fr.read())

    return d