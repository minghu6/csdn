# -*- coding:utf-8 -*-
#!/usr/bin/env python3

"""

"""
import time
import re

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from minghu6.etc.cmd import has_proper_chromedriver, has_proper_geckodriver
from minghu6.algs.dict import remove_key
from minghu6.etc.datetime import datetime_fromstr

from csdn_backup_common import read_blog_backup_log, write_blog_backup_log
from csdn_backup_common import EssayBrief

class WebDriverNotFoundError(BaseException):pass
def init_driver(driver_name=None, **kwargs):
    driver = None
    if driver_name is None:
        if has_proper_chromedriver():
            driver = webdriver.Chrome()
        elif has_proper_geckodriver():
            if 'profile_path' in kwargs:
                driver = webdriver.Firefox(firefox_profile=kwargs['profile_path'])
            else:
                driver = webdriver.Firefox()

    else:
        if driver_name == 'firefox':
            if has_proper_geckodriver():
                if 'profile_path' in kwargs:
                    driver = webdriver.Firefox(firefox_profile=kwargs['profile_path'])
                else:
                    driver = webdriver.Firefox()

        elif driver_name == 'chrome':
            if has_proper_chromedriver():
                driver = webdriver.Chrome()


    return driver

def login(driver, username, password):
    driver.get('https://passport.csdn.net/')

    elem_password = driver.find_element_by_name("password")
    elem_password.clear()
    elem_password.send_keys(password)

    elem_username = driver.find_element_by_name("username")
    elem_username.clear()
    elem_username.send_keys(username)

    elem_login_btn = driver.find_element_by_class_name('logging')

    elem_login_btn.submit()


def islogin(driver):

    driver.get('http://www.csdn.net/')
    elem_login = driver.find_elements_by_class_name('login')
    driver.back()

    if elem_login: # <span class="login"...> is findable, if not login in
        return False
    else:
        return True


def fetch_total_page_etc(driver, **kwargs):
    driver.get('http://write.blog.csdn.net/postlist')
    if driver.name == 'firefox':
        if 'asyn_time' in kwargs:
            time.sleep(kwargs['asyn_time'])
        else:
            time.sleep(1)


    essay_brief_set = set()
    for elem_essay in driver.find_elements_by_class_name('tdleft'):
        try:
            elem_a = elem_essay.find_element_by_tag_name('a')
            elem_span = elem_essay.find_element_by_tag_name('span')
        except NoSuchElementException:
            pass
        else:
            m = re.search("(?<=（).*(?=）)", elem_span.text)
            essay_datetime =  datetime_fromstr(m.group(0))
            essay_id = (elem_a.get_attribute('href').split('/')[-1])
            essay_brief_set.add(EssayBrief(essay_id, essay_datetime))


    elem_nav = driver.find_element_by_class_name('page_nav')
    text_total_page_num = elem_nav.find_element_by_tag_name('span').text

    pattern_total_page_num = r"(?<=共)\d+(?=页)"
    total_page_num_str = re.search(pattern_total_page_num, text_total_page_num).group(0)
    total_page_num = int(total_page_num_str)

    return total_page_num, essay_brief_set

def find_all_essay_brief(driver, end_page_num, start_page_num=2, ):
    essay_brief_set = set()
    for page_num_now in range(start_page_num, end_page_num+1):
        driver.get('http://write.blog.csdn.net/postlist/0/0/enabled/{0:d}'.format(page_num_now))
        for elem_essay in driver.find_elements_by_class_name('tdleft'):
            try:
                elem_a = elem_essay.find_element_by_tag_name('a')
                elem_span = elem_essay.find_element_by_tag_name('span')
            except NoSuchElementException:
                pass
            else:
                m = re.search("(?<=（).*(?=）)", elem_span.text)
                essay_datetime =  datetime_fromstr(m.group(0))
                essay_id = (elem_a.get_attribute('href').split('/')[-1])
                essay_brief_set.add(EssayBrief(essay_id, essay_datetime))

    return essay_brief_set

def download_md(driver, essay_brief_set, render_wait_time=0.5, **kwargs):
    #刷新恢复正常
    driver.refresh()
    first_download = True
    for essay_brief in essay_brief_set:
        driver.get('http://write.blog.csdn.net/mdeditor#!postId={0}'.format(essay_brief.id))
        if first_download:
            time.sleep(render_wait_time) # wait render

        if driver.name == 'firefox':
            if 'asyn_time' in kwargs:
                time.sleep(kwargs['asyn_time'])
            else:
                time.sleep(1)

        try:
            elem_step0 = driver.find_element_by_id('step-0')
        except NoSuchElementException:
            pass
        else:
            btn_0_cancel = elem_step0.find_elements_by_css_selector(".btn.btn-default")[0]
            btn_0_cancel.click()
            time.sleep(1)

        elem_a_export_doc = driver.find_elements_by_css_selector('.btn.btn-success.btn-export')[0]
        elem_a_export_doc.click()
        time.sleep(render_wait_time) # wait web page rending
        download_md = driver.find_elements_by_class_name('action-download-md')[0]
        download_md.click()
        if first_download:
            first_download = False
            if driver.name == 'firefox':
                input('set txt file download config, press any key to continue')


        #刷新恢复正常
        driver.refresh()

def logout(driver):
    #退出
    driver.get('https://passport.csdn.net/account/logout')


def backup_by_selenium(username, password,
                       from_datetime='1970-01-01 0:0:0', **kwargs):

    driver_name=kwargs.get('driver_name')
    kwargs = remove_key(kwargs, 'driver_name')
    driver = init_driver(driver_name=driver_name, **kwargs)

    if driver is None:
        raise WebDriverNotFoundError

    login(driver, username, password)
    if driver.name == 'firefox':
        if 'asyn_time' in kwargs:
            asyn_time = kwargs['asyn_time']
            time.sleep(asyn_time)
        else:
            time.sleep(1)


    total_page_num, essay_brief_set_page1 = fetch_total_page_etc(driver, **kwargs)
    essay_brief_set_other = find_all_essay_brief(driver, total_page_num)
    essay_brief_set = essay_brief_set_page1 | essay_brief_set_other

    last_blog_backup_datetime = read_blog_backup_log()
    essay_brief_set = filter(lambda item:item.datetime>last_blog_backup_datetime,
                             essay_brief_set)

    if 'render_wait_time' in kwargs:
        download_md(driver, essay_brief_set,
                    render_wait_time=kwargs['render_wait_time'], **kwargs)
    else:
        download_md(driver, essay_brief_set, **kwargs)

    write_blog_backup_log()