# -*- coding:utf-8 -*-
#!/usr/bin/env python3

"""

"""
import os

def offline(username, outdir=os.curdir, proxy_db=None):
    from .csdn_offline_aiohttp import offline as offline_aiohttp
    offline_aiohttp(username, outdir=os.curdir, proxy_db=None)


def fetch_page_list(username, outdir=os.curdir, proxy_db=None):
    from .csdn_offline_aiohttp import fetch_page_list as fetch_page_list_aio
    fetch_page_list_aio(username, outdir=os.curdir, proxy_db=None)
