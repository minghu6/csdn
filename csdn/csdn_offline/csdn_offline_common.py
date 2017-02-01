# -*- coding:utf-8 -*-
#!/usr/bin/env python3

"""

"""
from collections import namedtuple

from minghu6.internet.proxy_ip import proxy_ip
from minghu6.text.seq_enh import filter_invalid_char


URL_LIST_FILE_PATH = 'URList-{username:s}.txt'
UrlNameTuple = namedtuple('UrlNameTuple', ['url', 'title'])