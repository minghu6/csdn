# -*- coding:utf-8 -*-
#!/usr/bin/env python3

"""

"""
import datetime
from collections  import namedtuple
import os

from minghu6.etc.logger import SmallLogger
from minghu6.etc.datetime import datetime_fromstr


EssayBrief  = namedtuple('EssayBrief', ['id', 'datetime'])

def write_blog_backup_log(small_logger, failed_set=set(), d=datetime.datetime.now(), **kwargs):
    def format_essay_brief_w(section_name, elem, sep):
        if section_name == 'failed':
            formatted_str = '{id}{sep}{datetime}'.format(id=elem.id, sep=sep, datetime=elem.datetime.isoformat())
        elif section_name == 'last_time':
            formatted_str = '{datetime}'.format(datetime=elem.isoformat())
        else:
            formatted_str = str(elem)
        return formatted_str

    small_logger['last_time'] = [d]
    small_logger['failed'] = failed_set
    small_logger.write_log('.csdn_blog_log', format_func=format_essay_brief_w)


def read_blog_backup_log():
    small_logger = SmallLogger()
    if not os.path.exists('.csdn_blog_log'):
        small_logger['last_time'] = [datetime.datetime.fromtimestamp(0)]
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

        small_logger.read_log('.csdn_blog_log', format_func=format_essay_brief_r)

    return small_logger