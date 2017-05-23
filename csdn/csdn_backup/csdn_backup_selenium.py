# -*- coding:utf-8 -*-
# !/usr/bin/env python3

"""

"""
import http.cookiejar
import re
import time
import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
from minghu6.algs.userdict import remove_key
from minghu6.etc.version import islinux
from minghu6.etc.datetime import datetime_fromstr
from minghu6.etc.logger import SmallLogger

from .csdn_backup_common import EssayBrief
from .csdn_backup_common import read_blog_backup_log, write_blog_backup_log
from .csdn_backup_common import color, git_init, git_add, git_commit


class WebDriverNotFoundError(BaseException): pass


def init_driver(driver_name=None, **kwargs):

    def init_chrome(**kwargs):
        other_kwargs = {}
        # set driver path
        if 'driver_path' in kwargs:
            driver_path = kwargs['driver_path']
            other_kwargs['executable_path'] = driver_path

        # set download options
        if 'outdir' in kwargs:
            download_dir = kwargs['outdir']
        else:
            download_dir = os.curdir
        options = webdriver.ChromeOptions()
        download_dir = os.path.abspath(download_dir)
        prefs = {'profile.default_content_settings.popups': 0,
                 'download.default_directory': os.path.abspath(download_dir)}
        options.add_experimental_option('prefs', prefs)
        other_kwargs['chrome_options'] = options

        # start driver
        driver = webdriver.Chrome(**other_kwargs)
        return driver

    def init_firefox(**kwargs):
        other_kwargs = {}

        # set driver path
        if 'driver_path' in kwargs:
            driver_path = kwargs['driver_path']
            other_kwargs['executable_path'] = driver_path

        # set download options
        if 'outdir' in kwargs:
            download_dir = kwargs['outdir']
        else:
            download_dir = os.curdir
        profile = webdriver.FirefoxProfile()
        download_dir = os.path.abspath(download_dir)
        profile.set_preference('browser.download.dir', download_dir)
        # 0->desktop, 1->default folder, 2-> custom
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        # profile.set_preference('browser.helperApps.neverAsk.saveToDisk', '*'), .md file has no MIME Type
        # so we cann't set geckodriver driver to download silently

        # start driver
        driver = webdriver.Firefox(**other_kwargs)
        return driver

    if driver_name is None:
        driver = init_chrome(**kwargs)
    else:
        if driver_name == 'firefox':
            driver = init_firefox()
        elif driver_name == 'chrome':
            driver = init_chrome()
        else:
            driver = None
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


def construct_selenium_cookie(cookie: http.cookiejar.Cookie, **kwargs):
    cookie_dict = dict()
    cookie_dict['domain'] = cookie.domain
    cookie_dict['expiry'] = cookie.expires
    if 'httpOnly' in kwargs:
        cookie_dict['httpOnly'] = kwargs['httpOnly']
    else:
        cookie_dict['httpOnly'] = False

    cookie_dict['name'] = cookie.name
    cookie_dict['path'] = cookie.path
    cookie_dict['secure'] = cookie.secure
    cookie_dict['value'] = cookie.value

    return cookie_dict


def islogin(driver):
    driver.get('http://www.csdn.net/')
    elem_login = driver.find_elements_by_class_name('login')
    driver.back()

    if elem_login:  # <span class="login"...> is findable, if not login in
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
            essay_datetime = datetime_fromstr(m.group(0))
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
    for page_num_now in range(start_page_num, end_page_num + 1):
        driver.get('http://write.blog.csdn.net/postlist/0/0/enabled/{0:d}'.format(page_num_now))
        for elem_essay in driver.find_elements_by_class_name('tdleft'):
            try:
                elem_a = elem_essay.find_element_by_tag_name('a')
                elem_span = elem_essay.find_element_by_tag_name('span')
            except NoSuchElementException:
                pass
            else:
                m = re.search("(?<=（).*(?=）)", elem_span.text)
                essay_datetime = datetime_fromstr(m.group(0))
                essay_id = (elem_a.get_attribute('href').split('/')[-1])
                essay_brief_set.add(EssayBrief(essay_id, essay_datetime))

    return essay_brief_set


def download_md(driver, essay_brief_set, render_time=1, **kwargs):
    essay_brief_set = set(essay_brief_set)  # set(filter) then filter empty
    failed_set = set(essay_brief_set)
    outdir = kwargs['outdir']
    small_logger = SmallLogger()
    # 刷新恢复正常
    driver.refresh()
    first_download = True
    # print(essay_brief_set)
    for essay_brief in essay_brief_set:

        try:
            driver.get('http://write.blog.csdn.net/mdeditor#!postId={0}'.format(essay_brief.id))
            if first_download:
                time.sleep(render_time)  # wait render

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
                time.sleep(render_time)

            while True:
                try:
                    elem_a_export_doc = driver.find_elements_by_css_selector('.btn.btn-success.btn-export')[0]
                except IndexError:
                    print('wait .btn.btn-success.btn-export %.1f s'%render_time)
                    time.sleep(render_time)
                else:
                    break

            try:
                elem_a_export_doc.click()
            except ElementNotVisibleException:
                input('please Zoom the Browser Window to show the export-doc-btn\npress anykey to continue')
                elem_a_export_doc.click()

            time.sleep(render_time * 0.5)  # wait web page rending
            elem_download_md = driver.find_elements_by_class_name('action-download-md')[0]
            elem_download_md.click()
            repo_path = os.path.abspath(outdir)
            git_add(repo_path, ['*.md'])
            if first_download:
                first_download = False
                if driver.name == 'firefox':
                    input('press any key to continue,after(S)(A)')

        except Exception as ex:

            # print(ex)
            # traceback.print_stack()
            # return failed_set
            raise

        else:
            failed_set.remove(essay_brief)
            write_blog_backup_log(small_logger, failed_set=failed_set, outdir=outdir)
            # 刷新恢复正常
            driver.refresh()

    return failed_set


def logout(driver):
    # 退出
    driver.get('https://passport.csdn.net/account/logout')


def backup_by_selenium(username, password, **kwargs):
    driver_name = kwargs.get('driver_name')
    kwargs = remove_key(kwargs, 'driver_name')
    driver = init_driver(driver_name=driver_name, **kwargs)
    outdir = kwargs['outdir']
    small_logger = read_blog_backup_log(outdir=outdir)

    def firefox_wait():
        if driver.name == 'firefox':
            if 'asyn_time' in kwargs:
                time.sleep(kwargs['asyn_time'])
            else:
                time.sleep(1)

    if driver is None:
        raise WebDriverNotFoundError

    while True:
        login(driver, username, password)
        firefox_wait()
        if islogin(driver):
            break
        else:
            firefox_wait()
            print('retry login ...')

    if driver.name == 'firefox':
        if 'asyn_time' in kwargs:
            asyn_time = kwargs['asyn_time']
            time.sleep(asyn_time)
        else:
            time.sleep(1)

    total_page_num, essay_brief_set_page1 = fetch_total_page_etc(driver, **kwargs)
    essay_brief_set_other = find_all_essay_brief(driver, total_page_num)

    essay_brief_set = essay_brief_set_page1 | essay_brief_set_other
    last_blog_backup_datetime = small_logger['last_time'][0]
    if kwargs.get('backup_all', False):
        pass
    else:
        essay_brief_set = filter(lambda item: item.datetime > last_blog_backup_datetime,
                                 essay_brief_set)

    essay_brief_set = set(essay_brief_set)
    essay_brief_set |= set(small_logger['failed'])

    # init the git repo if not exists.
    repo_path = os.path.abspath(outdir)
    repo_dir, repo_name = os.path.split(repo_path)
    git_init(repo_name, repo_dir, force=False)
    try:
        download_md(driver, essay_brief_set, **kwargs)
    except:
        import traceback
        traceback.print_stack()
    finally:
        git_commit(repo_path, m='add md file by {0}'.format(driver.name))
