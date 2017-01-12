# -*- coding:utf-8 -*-
#!/usr/bin/env python3
"""
csdn

Usage:
  csdn <username> offline [--outdir=<outdir>] [--proxy_db=<proxy_db>]
  csdn <username> fetch-page-list [--proxy_db=<proxy_db>]

Options:
  <username>             userid
  -o --outdir=<outdir>   output directory of bake file [default: .]
  --proxy_db=<proxy_db>  point a proxy_db path(use minghu6.tools.proxy_ip
                                              to create.)
  fetch-page-list        only fetch the url-title page list

"""
import re
import os
from collections import namedtuple
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from minghu6.http.request import headers
from minghu6.text.seq_enh import filter_invalid_char
from minghu6.text.seq_enh import INVALID_FILE_CHAR_SET
from minghu6.internet.proxy_ip import proxy_ip
from minghu6.algs.decorator import singleton
from urllib.request import Request, urlopen
from docopt import docopt

URL_LIST_FILE_PATH = 'URList-{username:s}.txt'

EscapeCharsetMap = namedtuple('EscapeCharsetMap', ['html', 'url'])
@singleton
class EscapeCharsetMapClass:

    def __getitem__(self, char):
        hex_str = '{0:04x}'.format(ord(char))
        base_ten_str = '{0:03d}'.format(ord(char))
        return EscapeCharsetMap(url='%{0:s}'.format(hex_str),
                                html='&#{0:s}'.format(base_ten_str))

ESCAPED_CHARSET_MAP_DICT = EscapeCharsetMapClass()
def char_escape(s:str, escape_charset, escape_char_type:str):
    for each_escape_char in escape_charset:
        s=s.replace(each_escape_char,
                    getattr(ESCAPED_CHARSET_MAP_DICT[each_escape_char], escape_char_type))

    return s

def htmltitle2path(htmltitle, escape_char_type='url'):
    path=char_escape(htmltitle, INVALID_FILE_CHAR_SET, escape_char_type)
    path = ''.join(re.split('\s+', path)) # in case other blank char
    return path

html_num = None
url_name_tuple_set = set()
UrlNameTuple = namedtuple('UrlNameTuple', ['url', 'title'])
def fetch_url_title(username, proxy_db=None):
    print("Start Extracting Blog List...")
    url="http://blog.csdn.net/%s/article" % username

    try:
        response=urlopen(Request(url, headers=headers))
    except ConnectionRefusedError:
        res = proxy_ip.install_proxy_opener(test_url=url, dbname=proxy_db)
        if res==None:
            raise Exception('ConnectionRefusedError and There is no proper ip in proxy_db')

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

    file_path=URL_LIST_FILE_PATH.format(username=username)
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
    for i in range(2, page_num+1):
        next_page_url = 'http://blog.csdn.net/{0}/article/list/{1}'.format(username, i)
        response=urlopen(Request(next_page_url, headers=headers))
        html=response.read()
        bsObj = BeautifulSoup(html, 'html.parser')

        add_and_write(bsObj, url_name_tuple_set, csvwriter)

    csvfw.close()


def download(username='minghu9'):
    dirname = 'CSDN-'+username
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    n = html_num
    print('total {0:d} items'.format(n))
    while True:
        if n == 0:
            break
        try:
            url_name = url_name_tuple_set.pop()
            n -= 1
        except KeyError:
            pass
        else:
            path = os.path.join(dirname, htmltitle2path(url_name.title)+'.html')
            response=urlopen(Request(url=url_name.url, headers=headers))
            with open(path, 'wb') as fw:
                fw.write(response.read())

            print(("Successfully Downloaded "+url_name.title))


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
def generate_index(username='minghu9'):
    file_path=URL_LIST_FILE_PATH.format(username=username)
    f=open(file_path,'r',encoding='utf-8')
    fout=open('Index_{0}.html'.format(username),'w',encoding='utf-8')
    fout.write(index_head_string)
    fout.write("""<h2>"""+username+"的博客"+"""</h2>\n""")
    fout.write("""<ol>\n""")
    for line in f.readlines():
        m=re.search('(http.+[0-9]{7,}),(.+)',line)
        title=m.group(2)
        #print(title)
        fout.write("""<li><a href=\""""+'./CSDN-'+username+'/'+title+".html"+"""\">"""+title+"""</a></li>\n""")
    fout.write("""</ol>""")
    fout.write(index_tail_string)
    f.close()
    fout.close()


def main(username, proxy_db=None):

    fetch_url_title(username, proxy_db)
    print("Start Downloading Blog List...")
    download(username)
    print("Start Generating Index.html...")
    generate_index(username)
    print("Done.")

def interactive():
    arguments = docopt(__doc__)

    if arguments['offline']:
        username = arguments['<username>']
        #print(arguments['--outdir'], username)
        if arguments['--proxy_db'] != None:
            proxy_db = None
        else:
            proxy_db = arguments['--proxy_db']

        main(username=username, proxy_db=proxy_db)
    elif arguments['fetch-page-list']:
        username = arguments['<username>']
        #print(arguments['--outdir'], username)
        if arguments['--proxy_db'] != None:
            proxy_db = None
        else:
            proxy_db = arguments['--proxy_db']

        fetch_url_title(username, proxy_db)

if __name__=='__main__':
    interactive()