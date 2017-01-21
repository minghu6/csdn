# -*- coding:utf-8 -*-
#!/usr/bin/env python3
"""
csdn

Usage:
  csdn <username> offline [--outdir=<outdir>] [--proxy_db=<proxy_db>]
  csdn <username> fetch-page-list [--proxy_db=<proxy_db>]
  csdn <username> backup <password> [--render-time=<render_time>] [--firefox]
                                    [--asyn-time=<asyn_time>] [--load-profile=<profile-path>]

Options:
  <username>                     userid
  -o --outdir=<outdir>           output directory of bake file [default: .]
  --proxy_db=<proxy_db>          point a proxy_db path(use minghu6.tools.proxy_ip
                                 to create.)
  fetch-page-list                only fetch the url-title page list
  --render_time=<render_time>    render time when load a page in webdriver
  --firefox                      using geckodriver
  --asyn_time=<asyn_time>        some driver like geckodriver return before page loaderd completely,
                                 so, we need wait some time [default: 1] (s).
  --load-profile=<profile-path>  profile path (for geckodriver)

"""
from .csdn_offline.csdn_offline import offline, fetch_page_list
from .csdn_backup.csdn_backup  import blog_backup
from docopt import docopt


def interactive():
    arguments = docopt(__doc__)

    if arguments['offline']:
        username = arguments['<username>']
        #print(arguments['--outdir'], username)
        proxy_db = arguments['--proxy_db']

        outdir = arguments['--outdir']

        offline(username=username, outdir=outdir, proxy_db=proxy_db)

    elif arguments['fetch-page-list']:
        username = arguments['<username>']
        #print(arguments['--outdir'], username)
        proxy_db = arguments['--proxy_db']

        outdir = arguments['--outdir']
        fetch_page_list(username, outdir, proxy_db)

    elif arguments['backup']:
        username = arguments['<username>']
        password = arguments['<password>']

        other_kwargs = {}
        if arguments['--render-time']:
            render_time = float(arguments['--render-time'])
            other_kwargs['render_time'] = render_time

        if arguments['--firefox']:
            driver_name = 'firefox'
            other_kwargs['driver_name'] = driver_name

        if arguments['--asyn-time']:
            asyn_time = float(arguments['--asyn-time'])
            other_kwargs['asyn_time'] = asyn_time

        if arguments['--load-profile']:
            profile_path = arguments['--load-profile']
            other_kwargs['profile_path'] = profile_path

        blog_backup(username, password, **other_kwargs)




if __name__=='__main__':
    interactive()