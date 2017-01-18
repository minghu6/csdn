# -*- coding:utf-8 -*-
#!/usr/bin/env python3
"""
csdn

Usage:
  csdn <username> offline [--outdir=<outdir>] [--proxy_db=<proxy_db>]
  csdn <username> fetch-url-title [--proxy_db=<proxy_db>]
  csdn <username> backup <password> [--render_time=<render_time>]

Options:
  <username>                   userid
  -o --outdir=<outdir>         output directory of bake file [default: .]
  --proxy_db=<proxy_db>        point a proxy_db path(use minghu6.tools.proxy_ip
                               to create.)
  fetch-page-list              only fetch the url-title page list
  --render_time=<render_time>  render time when load a page in webdriver

"""
from docopt import docopt

from csdn_offline import offline, fetch_url_title
from csdn_backup  import blog_backup



def interactive():
    arguments = docopt(__doc__)

    if arguments['offline']:
        username = arguments['<username>']
        #print(arguments['--outdir'], username)
        proxy_db = arguments['--proxy_db']

        outdir = arguments['--outdir']

        offline(username=username, outdir=outdir, proxy_db=proxy_db)

    elif arguments['fetch-url-title']:
        username = arguments['<username>']
        #print(arguments['--outdir'], username)
        proxy_db = arguments['--proxy_db']

        outdir = arguments['--outdir']
        fetch_url_title(username, outdir, proxy_db)

    elif arguments['backup']:
        username = arguments['<username>']
        password = arguments['<password>']

        other_kwargs = {}
        if arguments['--render_time']:
            render_time = float(arguments['--render_time'])
            other_kwargs['render_time'] = render_time

        blog_backup(username, password, **other_kwargs)




if __name__=='__main__':
    interactive()