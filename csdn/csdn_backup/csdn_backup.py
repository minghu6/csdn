# -*- coding:utf-8 -*-
#!/usr/bin/env python3

"""

"""

def blog_backup(username, password, **kwargs):

    from csdn.csdn_backup.csdn_backup_selenium import backup_by_selenium
    backup_by_selenium(username, password, **kwargs)


