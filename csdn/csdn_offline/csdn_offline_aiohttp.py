# -*- coding:utf-8 -*-
#!/usr/bin/env python3

"""

"""
import asyncio
import csv
import os
import re
from itertools import repeat
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import aiohttp
import async_timeout
from bs4 import BeautifulSoup
from .csdn_offline_common import URL_LIST_FILE_PATH
from .csdn_offline_common import UrlNameTuple
from .csdn_offline_common import htmltitle2path
from minghu6.http.request import headers
from minghu6.text.seq_enh import filter_invalid_char


class AsyncIteratorWrapper:
    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value

html_num = None
url_name_tuple_set = set()

async def fetch(session, url):
        with async_timeout.timeout(20):
            async with session.get(url) as response:
                return await response.read()

async def fetch_url_title(username, loop, outdir=os.curdir, proxy_db=None):

    print("Start Extracting Blog List...")

    url="http://blog.csdn.net/%s/article" % username

    try:
        response=urlopen(Request(url, headers=headers))

    except ConnectionRefusedError:
        raise
        #res=proxy_ip.install_proxy_opener(test_url=url)
        #if res==None:
        #    raise Exception('ConnectionRefusedError and There is no proper ip in proxy_db')

    html=response.read()
    bsObj = BeautifulSoup(html, 'html.parser')

    # get total item number and total page number
    page_raw_string=bsObj.find_all(name='div', attrs={'class' : 'pagelist'})[0].span.text

    page_num_pattern = '(?<=共).*(?=页)'
    page_num_str=re.search(page_num_pattern, page_raw_string).group(0)
    page_num = int(page_num_str) #total item number

    item_num_pattern = '.*(?=条)'
    item_num_str=re.search(item_num_pattern, page_raw_string).group(0)
    item_num = int(item_num_str) # total page number
    global html_num
    html_num = item_num

    if page_num < 1:
        return # zero page error

    file_path=os.path.join(outdir, URL_LIST_FILE_PATH.format(username=username))
    csvfw=open(file_path, 'w', encoding='utf-8', newline='')
    csvwriter = csv.writer(csvfw, delimiter=',')
    def add_and_write(bsObj, url_name_tuple_set, csvwriter):
        for item in bsObj.find_all(name='span', attrs={'class' : 'link_title'}):
            item_name = filter_invalid_char(item.text, {"\n", "\r"})
            item_name = item_name.strip()
            item_url = urljoin(url, item.a['href'])

            url_name_tuple = UrlNameTuple(item_url, item_name)
            #print(url_name_tuple)
            url_name_tuple_set.add(url_name_tuple)
            csvwriter.writerow(url_name_tuple) # web io is much slower than local io

    add_and_write(bsObj, url_name_tuple_set, csvwriter)
    session = aiohttp.ClientSession(loop=loop, headers=headers)
    async for i in AsyncIteratorWrapper(range(2, page_num+1)):

        next_page_url = 'http://blog.csdn.net/{0}/article/list/{1}'.format(username, i)
        content = await fetch(session, next_page_url)

        #html = ''.join(list(response.read()))
        bsObj = BeautifulSoup(content, 'html.parser')

        add_and_write(bsObj, url_name_tuple_set, csvwriter)

    csvfw.close()
    session.close()


async def download(username, loop, outdir=os.curdir):
    print("Start Downloading Blog List...")
    dirname = os.path.join('CSDN-'+username)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    n = html_num
    print('total {0:d} items'.format(n))
    session = aiohttp.ClientSession(loop=loop, headers=headers)
    async for i in AsyncIteratorWrapper(repeat(0)):
        if n == 0:
            break
        try:
            url_name = url_name_tuple_set.pop()
            n -= 1
        except KeyError:
            pass
        else:
            path = os.path.join(dirname, htmltitle2path(url_name.title)+'.html')
            content = await fetch(session, url_name.url)

            with open(path, 'wb') as fw:
                fw.write(content)

            print(("Successfully Downloaded "+url_name.title))

    session.close()

index_head_string="""
<html>
<head>
  <title>Evernote Export</title>
  <basefont face="微软雅黑" size="2" />
  <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
  <meta name="exporter-version" content="Evernote Windows/276127; Windows/6.3.9600;"/>
  <style>
    body, td {
      font-family: 微软雅黑;
      font-size: 10pt;
    }
  </style>
</head>
<body>
"""
index_tail_string="""
</body>
</html>
"""
def generate_index(username, outdir=os.curdir):
    print("Start Generating Index.html...")
    file_path=os.path.join(outdir, URL_LIST_FILE_PATH.format(username=username))
    f=open(file_path,'r', encoding='utf-8')
    fout=open('Index_{0}.html'.format(username),'w',encoding='utf-8')
    fout.write(index_head_string)
    fout.write("""<h2>"""+username+"的博客"+"""</h2>\n""")
    fout.write("""<ol>\n""")
    for line in f.readlines():
        m=re.search('(http.+[0-9]{7,}),(.+)',line)
        title=m.group(2)
        #print(title)
        fout.write("""<li><a href=\""""+'./CSDN-'+username+'/'+htmltitle2path(title)+".html"+"""\">"""+title+"""</a></li>\n""")
    fout.write("""</ol>""")
    fout.write(index_tail_string)
    f.close()
    fout.close()


def offline(username, outdir=os.curdir, proxy_db=None):
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(fetch_url_title(username,
                                              loop,
                                              outdir,
                                              proxy_db)),

        asyncio.ensure_future(download(username,
                                       loop,
                                       outdir))
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    generate_index(username)


def fetch_page_list(username, outdir=os.curdir, proxy_db=None):


    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_url_title(username,
                                            loop,
                                            outdir,
                                            proxy_db))
