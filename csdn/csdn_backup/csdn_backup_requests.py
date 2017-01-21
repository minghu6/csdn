# -*- coding:utf-8 -*-
#!/usr/bin/env python3

"""

"""
import requests
from minghu6.http.request import headers
from bs4 import BeautifulSoup

def login(username, password, session=None):
    if session is None:
        session=requests.Session()

    login_url='https://passport.csdn.net/account/login'
    r=session.get(login_url, headers=headers)
    bsObj = BeautifulSoup(r.content, 'html.parser')

    lt = bsObj.find_all(name='input',
                        attrs={'name': 'lt'})[0]['value']
    execution = bsObj.find_all(name='input',
                               attrs={'name': 'execution'})[0]['value']
    _eventId = bsObj.find_all(name='input',
                              attrs={'name': '_eventId'})[0]['value']
    params = {'username': 'a19678zy@163.com',
        'password': '19678zy',
         'lt': lt,
         'execution': execution,
         '_eventId': _eventId,
         #'login': ''
        }
    r=session.post(login_url, data=params, headers=headers)
    return session, r


def logout(session):
    r=session.get('https://passport.csdn.net/account/logout')
    return session, r