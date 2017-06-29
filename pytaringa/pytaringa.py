# -*- coding: utf-8 -*-

from functools import wraps
from datetime import datetime
import re
import json
import requests
import time
import os
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
        self.user_id = None
        self.username = username
        self.password = password
        self.base_url = BASE_URL
        self.api_url = API_URL
        self.realtime = None

        if self.cookie is None:
            self.login()
            self.store_user_key()
            self.store_user_id()
            self.store_realtime_data()

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
            raise TaringaException('Login failed: Request was not succesful')
            return

        response = json.loads(request.text)

        if not response.get('status'):
            raise TaringaException('Login failed: Wrong auth data?')
        else:
            cookie = {}

            cookie['ln'] = request.cookies.get('ln', '')
            cookie['tid'] = request.cookies.get('tid', '')
            cookie['trngssn'] = request.cookies.get('trngssn', '')

            self.cookie = cookie
            debug('Logged in succesfuly as %s' % self.username)

    @user_logged_in
    def store_user_id(self):
        self.user_id = self.cookie.get('tid').rsplit('%3A%3A')[0]
        self.cookie.update({'user_id': self.user_id})

    @user_logged_in
    def store_realtime_data(self):
        regex = r"new Realtime\({\"host\":\"(.*?)\",\"port\":(\d+),\"useSSL\":true}(?:.+) notifications\('([a-z0-9]+)"
        request = TaringaRequest(cookie=self.cookie).get_request(self.base_url)

        realtime = re.findall(regex, request.text, re.DOTALL)
        if len(realtime) > 0:
            if len(realtime[0]) == 2:
                self.realtime = realtime[0]
            else:
                raise TaringaException('Login failed: Wrong auth data?')
        else:
            raise TaringaException('Login failed: Wrong auth data?')
            
    @user_logged_in
    def store_user_key(self):
        regex = r'var global_data = { user: \'.*?\', user_key: \'(.*?)\''
        request = TaringaRequest(cookie=self.cookie).get_request(self.base_url)

        user_key = re.findall(regex, request.text, re.DOTALL)

        if len(user_key) > 0:
            self.user_key = user_key[0]
            self.cookie.update({'user_key': user_key[0]})
        else:
            return debug('Could not obtain user_key')

    @user_logged_in
    def get_url(self,url):
        request = TaringaRequest(cookie=self.cookie).get_request(self.base_url + "/" + url)

    def get_user_id_from_nick(self, user_nick):
        url = self.api_url + '/user/nick/view/%s' % user_nick
        request = TaringaRequest().get_request(url)
        response = json.loads(request.text)
        if "code" in response:
            return None
        else:
            return response["id"]

    def follow_user(self, user_id):
        data = {
            'key': self.cookie.get('user_key'),
            'type':'user',
            'obj':str(user_id),
            'action':'follow'
        }

        url = self.base_url + '/notificaciones-ajax.php'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)

    def get_wallpost(self, link):
        regex = r'<div class=\"activity-content\">(?:\s+)<span class=\"dialog\"></span>(?:\s+)<div class=\"activity-header clearfix\">(?:\s+)@<a class="hovercard"(?:.*?)<\/div>(?:\s+)<p>(.*?)<\/p>'
        url = self.base_url + link
        request = TaringaRequest(cookie=self.cookie).get_request(url)

        content = re.findall(regex, request.text, re.MULTILINE | re.DOTALL)

        if len(content) > 0:
            return content[0]
        else:
            debug('Could not obtain the wallpost content')
            return None

    def get_replies_comment(self, comment_id, obj_id, obj_owner,obj_type):
        data = {
            'key': self.cookie.get('user_key'),
            'objectType':obj_type,
            'objectId':obj_id,
            'objectOwner':obj_owner,
            'commentId':comment_id,
            'page':'-200'
        }

        url = self.base_url + '/ajax/comments/get-replies'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)
        response = json.loads(request.text)
        if "code" in response:
            return None
        else:
            return response

    def get_signature_comment(self, comment_id, obj_id,obj_type):
        data = {
            'key': self.cookie.get('user_key'),
            'objectType':obj_type,
            'objectId':obj_id,
            'commentId':comment_id,
        }
        regex = r'<div class=\"comment clearfix(?:.*?)\" data-id="(?:\d+)"(?:.*?)data-signature="(.*?)"'
        url = self.base_url + '/ajax/comments/get'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)
        content = re.findall(regex, request.text, re.DOTALL)

        if len(content) > 0:
            return content[0]
        else:
            debug('Could not obtain the signature')
            return None


class Shout(object):
    def __init__(self, cookie):
        self.cookie = cookie
        self.base_url = BASE_URL
        self.api_url = API_URL

    @user_logged_in
    def add(self, body, type_shout=0, privacy=0, attachment=''):
        data = {
            'key': self.cookie.get('user_key'),
            'attachment': attachment,
            'attachment_type': type_shout,
            'privacy': privacy,
            'body': body
        }

        url = self.base_url + '/ajax/shout/add'
        regex = r'</i>.*?<a href="(.*?)" title="Hace instantes"'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)
        urlshout = re.findall(regex, request.text, re.DOTALL)
        if len(urlshout) > 0:
            return "http://www.taringa.net" + urlshout[0]
        else:
            return debug('Could not obtain shout url')

    @user_logged_in
    def add_comment(self, comment, obj_id, obj_owner, obj_type):
        data = {
            'key': self.cookie.get('user_key'),
            'comment': comment,
            'objectId': obj_id,
            'objectOwner': obj_owner,
            'objectType': obj_type,
            'show':'true'
        }
        url = self.base_url + '/ajax/comments/add'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)

    def add_reply_comment(self, comment, obj_id, obj_owner, obj_type, parent, parentOwner,signature):
        data = {
            'key': self.cookie.get('user_key'),
            'comment': comment,
            'objectId': obj_id,
            'objectOwner': obj_owner,
            'objectType': obj_type,
            'show':'true',
            'parent':parent,
            'parentOwner':parentOwner,
            'signature':signature

        }
        url = self.base_url + '/ajax/comments/add'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)
        
    @user_logged_in
    def like(self, shout_id, owner_id):
        data = {
            'key': self.cookie.get('user_key'),
            'owner': owner_id,
            'uuid': shout_id,
            'score': '1'
        }

        url = self.base_url + '/ajax/shout/vote'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)
        response = json.loads(request.text)
        if response["status"] == 1:
            return 1
        else:
            return "0 " + response["data"]

    def delete(self, shout_id):
        data = {
            'owner': self.cookie.get('user_id'),
            'key': self.cookie.get('user_key'),
            'id': shout_id
        }

        url = self.base_url + '/ajax/shout/delete'
        TaringaRequest(cookie=self.cookie).post_request(url, data=data)

    def get_object(self, shout_id):
        url = self.api_url + '/shout/view/%s' % shout_id
        request = TaringaRequest().get_request(url)
        response = json.loads(request.text)

        return response

    def get_last_shout_from_id(self, user_id):
        url = self.api_url + '/shout/user/view/%s?trim_user=true' % user_id
        request = TaringaRequest().get_request(url)
        response = json.loads(request.text)

        if "code" in response:
            return None
        else:
            for shout in response:
                if shout["owner"] == str(user_id):
                    return shout["id"]
            return None


class Kn3(object):
    @staticmethod
    def import_to_kn3(url):
        request = requests.get(url, stream=True)
        if request.status_code == 200:
            temp_name = str(time.time())
            with open(temp_name, 'wb') as f:
                for chunk in request.iter_content(1024):
                    f.write(chunk)
            upload = Kn3.upload(temp_name)
            os.remove(temp_name)
            if not upload:
                debug("Could not upload image")
                return "Could not upload image"
            else:
                return upload

    @staticmethod
    def upload(filename):
        kn3Url = "http://kn3.net/upload.php"
        files = {'files[]': open(filename, 'rb')}
        r = requests.post(kn3Url,files=files)
        if r.status_code == 200:
            response = json.loads(r.text)
            return response["direct"]
        else:
            return None
