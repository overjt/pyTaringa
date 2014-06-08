#! /usr/bin/env python
# -*- coding:Utf-8 -*-


from functools import wraps
from datetime import datetime

import re
import json
import requests

USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:29.0) '
USER_AGENT += 'Gecko/20100101 Firefox/29.0'

HEADERS = {'Referer': 'http://www.taringa.net',
           'User-Agent': USER_AGENT}


def debug(message):
    now = datetime.now()
    str_out = '[%s]: %s' % (now.strftime('%d-%m-%Y %H:%M'), message)

    print str_out


def response_successful(f):
    @wraps(f)
    def inner(*args, **kwargs):
        response = f(*args, **kwargs)

        if response and response.status_code == 200:
            return response
        else:
            raise TaringaRequestException('Response was not succesful')
    return inner


class TaringaException(Exception):
    def __init__(self, message):
        debug(message)


class TaringaRequestException(Exception):
    def __init__(self, message):
        debug(message)


class TaringaRequest(object):
    def __init__(self, headers=HEADERS, cookie=None):
        self.headers = headers
        self.cookie = cookie

    @response_successful
    def get_request(self, url):
        if self.cookie:
            request = requests.get(url, headers=self.headers,
                                   cookies=self.cookie)
        else:
            request = requests.get(url, headers=self.headers)

        return request

    @response_successful
    def post_request(self, url, data):
        if self.cookie:
            request = requests.post(url, cookies=self.cookie,
                                    headers=self.headers, data=data)
        else:
            request = requests.post(url, headers=self.headers, data=data)

        return request


class Taringa(object):
    def __init__(self, username=None, password=None, cookie=None,
                 user_key=None):
        self.cookie = cookie
        self.user_key = user_key

        self.username = username
        self.password = password
        self.base_url = 'http://www.taringa.net'

        if self.cookie is None:
            self.login()
            self.get_user_key()

    def login(self):
        data = {
            'connect': '',
            'redirect': '/',
            'nick': self.username,
            'pass': self.password
        }

        url = self.base_url + '/registro/login-submit.php'

        try:
            request = TaringaRequest().post_request(url, data)
        except TaringaRequestException:
            debug('Login failed: Request was not succesful')
            return

        response = json.loads(request.text)

        if not response.get('status'):
            raise TaringaException('Login failed: Wrong auth data?')
        else:
            cookie = {}

            cookie['ln'] = request.cookies.get('ln', '')
            cookie['tid'] = request.cookies.get('tid', '')
            cookie['trnssn'] = request.cookies.get('trnssn', '')

            self.cookie = cookie

            debug('Logged in succesfuly as %s' % self.username)

    def get_user_id(self):
        if self.cookie:
            self.user_id = self.cookie.get('tid').rsplit('%3A%3A')[0]

    def get_user_key(self):
        regex = r'var global_data = { user: \'.*?\', user_key: \'(.*?)\''
        request = TaringaRequest(cookie=self.cookie).get_request(self.base_url)

        user_key = re.findall(regex, request.text, re.DOTALL)

        if len(user_key) > 0:
            self.user_key = user_key[0]
            return user_key[0]
        return debug('Could not obtain user_key')

    def shout(self, body, type=0, privacy=0, attachment=''):
        data = {
            'attachment': attachment,
            'attachment_type': 0,
            'body': body,
            'key': self.user_key,
            'privacy': privacy
        }

        url = self.base_url + '/ajax/shout/add'
        request = TaringaRequest(cookie=self.cookie).\
            post_request(url, data=data)

        if body in request.text:
            debug('Shout succesful')
        else:
            debug('Something went wrong')

    def get_user_id_from_nick(self, user_nick):
        pass
        # to implement

    def like_shout(self, shout_id, owner_id):
        pass
        # to implement

    def delete_shout(self, shout_id):
        pass
        # to implement

    def get_shout_body(self, shout_id):
        pass
        # to implement

    def get_user_lastest_shout(self, user_id):
        pass
        # to implement

    def import_to_kn3(self, url):
        pass
        # to implement
