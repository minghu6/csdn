# -*- coding:utf-8 -*-
#!/usr/bin/env python3

"""

"""

def blog_backup(username, password, from_datetime='1970-01-01 0:0:0', **kwargs):

    from csdn_backup_selenium import backup_by_selenium, WebDriverNotFoundError
    backup_by_selenium(username, password, from_datetime, **kwargs)


