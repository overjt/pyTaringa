#! /usr/bin/env python
# -*- coding:Utf-8 -*-


from functools import wraps
from datetime import datetime

import re
import json
import requests

USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:29.0) '
USER_AGENT += 'Gecko/20100101 Firefox/29.0'

BASE_URL = 'http://www.taringa.net'
API_URL = 'http://api.taringa.net'

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


def user_logged_in(fun):
    def inner(self, *args, **kwargs):
        if self.cookie:
            return fun(self, *args, **kwargs)
    return inner


class Taringa(object):
    def __init__(self, username=None, password=None, cookie=None,
                 user_key=None):
        self.cookie = cookie
        self.user_key = user_key

        self.username = username
        self.password = password
        self.base_url = BASE_URL
        self.api_url = API_URL

        if self.cookie is None:
            self.login()
            self.store_user_key()
            self.stostore_user_id()

    def login(self):
        data = {
            'nick': self.username,
            'pass': self.password,
            'redirect': '/',
            'connect': ''
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

    @user_logged_in
    def store_user_id(self):
        user_id = self.cookie.get('tid').rsplit('%3A%3A')[0]
        self.cookie.update({'user_id': user_id})

    @user_logged_in
    def store_user_key(self):
        regex = r'var global_data = { user: \'.*?\', user_key: \'(.*?)\''
        request = TaringaRequest(cookie=self.cookie).get_request(self.base_url)

        user_key = re.findall(regex, request.text, re.DOTALL)

        if len(user_key) > 0:
            self.cookie.update({'user_key': user_key[0]})
        return debug('Could not obtain user_key')

    def get_user_id_from_nick(self, user_nick):
        url = self.api_url + '/user/nick/view/%s' % user_nick
        request = TaringaRequest().get_request(url)
        response = json.loads(request.text)

        return response


class Shout(object):
    def __init__(self, cookie):
        self.cookie = cookie
        self.base_url = BASE_URL
        self.api_url = API_URL

    @user_logged_in
    def add(self, body, type=0, privacy=0, attachment=''):
        data = {
            'key': self.cookie.get('key'),
            'attachment': attachment,
            'attachment_type': 0,
            'privacy': privacy,
            'body': body
        }

        url = self.base_url + '/ajax/shout/add'
        TaringaRequest(cookie=self.cookie).post_request(url, data=data)

    def like(self, shout_id, owner_id):
        data = {
            'key': self.cookie.get('key'),
            'owner': owner_id,
            'uuid': shout_id,
            'score': '1'
        }

        url = self.base_url + '/ajax/shout/vote'
        TaringaRequest(cookie=self.cookie).post_request(url, data=data)

    def delete(self, shout_id):
        data = {
            'owner': self.cookie.get('user_id'),
            'key': self.cookie.get('key'),
            'id': shout_id
        }

        url = self.base_url + '/ajax/shout/delete'
        TaringaRequest(cookie=self.cookie).post_request(url, data=data)

    def get_object(self, shout_id):
        url = self.api_url + '/shout/view/%s' % shout_id
        request = TaringaRequest().get_request(url)
        response = json.loads(request.text)

        return response


class Kn3(object):
    @staticmethod
    def import_to_kn3(url):
        pass
        # to implement
