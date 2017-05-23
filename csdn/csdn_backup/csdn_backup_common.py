# -*- coding:utf-8 -*-
#!/usr/bin/env python3

"""

"""
import datetime
from collections  import namedtuple
import os

from minghu6.etc.logger import SmallLogger
from minghu6.etc.datetime import datetime_fromstr
from minghu6.etc.git import git_init, git_add, git_commit
from minghu6.text.color import color

EssayBrief = namedtuple('EssayBrief', ['id', 'datetime'])


def write_blog_backup_log(small_logger,
                          failed_set=set(),
                          d=datetime.datetime.now(),
                          outdir=os.curdir,
                          **kwargs):

    def format_essay_brief_w(section_name, elem, sep):
        if section_name == 'failed':
            formatted_str = '{id}{sep}{datetime}'.format(id=elem.id,
                                                         sep=sep,
                                                         datetime=elem.datetime.isoformat())
        elif section_name == 'last_time':
            formatted_str = '{datetime}'.format(datetime=elem.isoformat())
        else:
            formatted_str = str(elem)
        return formatted_str

    small_logger['last_time'] = [d]
    small_logger['failed'] = failed_set
    logpath = os.path.abspath(os.path.join(outdir, '.csdn_blog_log'))
    small_logger.write_log(logpath, format_func=format_essay_brief_w)

def read_blog_backup_log(outdir=os.curdir):
    small_logger = SmallLogger()
    logpath = os.path.abspath(os.path.join(outdir, '.csdn_blog_log'))
    if not os.path.exists(logpath):
        # fromtimestamp(0) maybe failed on win32, unless use tz.tzwinloacl()
        small_logger['last_time'] = [datetime.datetime.utcfromtimestamp(0)]
        small_logger['failed'] = set()

    else:
        def format_essay_brief_r(section_name, line, sep):
            if section_name == 'failed':
                elem_list = line.split(sep)
                essay_id = elem_list[0]
                essay_datetime = datetime_fromstr(elem_list[1], sep_date_time='T')
                elem = EssayBrief(id=essay_id, datetime=essay_datetime)
            elif section_name == 'last_time':
                elem = datetime_fromstr(line, sep_date_time='T')
            else:
                elem = line

            return elem

        small_logger.read_log(logpath, format_func=format_essay_brief_r)

    return small_logger


