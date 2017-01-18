# -*- coding:utf-8 -*-
#!/usr/bin/env python3

"""

"""

def blog_bakeup(username, password, from_datetime='1970-01-01 0:0:0', **kwargs):
    from .csdn_bakeup_selenium import bakeup_by_selenium, WebDriverNotFoundError
    bakeup_by_selenium(username, password, from_datetime, **kwargs)


