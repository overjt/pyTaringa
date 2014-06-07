# -*- coding: utf-8 -*-
import urllib
import urllib2
from cookielib import Cookie
from cookielib import CookieJar
import json


class pyTaringa(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.user_key = None
        self.user_id = None
        self.cookie = None
        self.cookiejar = CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.89 Safari/537.36')]
        self.login()
        if self.cookie is not None:
            self.getId()
            self.getUserKey()

    def login(self):
        data = {
                        'connect':'',
                        '':'',
                        'nick': self.username,
                        'pass': self.password
                        }
        request = self.httpRequest('registro/login-submit.php', data, True)
        response = json.loads(request)
        if response["status"] == 1:
            for cookie in self.cookiejar:
                if cookie.name == "tid":
                    self.cookie = cookie.value
                    break
            fbCookie = Cookie(0, 'fbs', "false", None, None, 'www.taringa.net', True, False, '/', True, False, None, False, None, None, None)
            twCookie = Cookie(0, 'tws', "false", None, None, 'www.taringa.net', True, False, '/', True, False, None, False, None, None, None)
            self.cookiejar.set_cookie(fbCookie)
            self.cookiejar.set_cookie(twCookie)

    def extractText(self, string, delimiter1, delimiter2):
        ''' Función improvisada para evitar el uso de expresiones regulares xD '''
        pos = string.find(delimiter1) 
        if pos == -1:
            return None
        pos2 = string.find(delimiter2, pos + len(delimiter1))
        if pos2 == -1:
            return None
        return string[pos+ len(delimiter1):pos2]

    def getId(self):
        if self.cookie is not None:
            self.user_id = self.cookie.split("%3A%3A")[0]

    def getUserKey(self):
        request = self.httpRequest('')
        key = self.extractText(request, "user_key: '", "'")
        if key is not None:
            self.user_key = key

    def shout(self, text, type=0, attachment=''):
        params = {
                  'body': str(text),
                  'privacy': 0,
                  'key': self.user_key,
                  'attachment_type': type,  # 1 para imagenes, 0 para texto, 3 para links de taringa
                  'attachment': str(attachment)  # la direccion del attachment
                  }
        request = self.httpRequest('ajax/shout/add', params)
        urlShout = self.extractText(request.replace("\t","").replace("\n",""), "</i><a href=\"", "\" title=\"Hace instantes\"")
        if urlShout is not None:
            return "http://www.taringa.net" + urlShout
        else:
            return request

    def shoutText(self, text):
        return self.shout(text)

    def shoutImage(self, text, imageUrl):
        kn3Image = self.importToKn3(imageUrl)
        if kn3Image is not None:            
            return self.shout(text, 1, kn3Image)
        else:
            return False

    def getUserId(self, user_nick):
        request = self.httpRequest('user/nick/view/' + str(user_nick),None,False,True)
        response = json.loads(request)
        if "code" in response:
            return None
        else:
            return response["id"]


    def likeShout(self, shout_id, owner_id):
        params = {
                    'uuid': int(shout_id),
                    'owner': int(owner_id),
                    'score': 1,
                    'key': self.user_key
                    }
        request = self.httpRequest("ajax/shout/vote",params)
        response = json.loads(request)
        if response["status"] == 1:
            return 1
        else:
            return "0 " + response["data"]

    def deleteShout(self, shout_id):
        params = {
                    'id': int(shout_id),
                    'owner': self.user_id,
                    'key': self.user_key
                    }
        #TODO: verificar la respuesta para evitar posibles errores
        request = self.httpRequest("ajax/shout/delete",params)


    def getShoutText(self, shout_id):
        request = self.httpRequest('shout/view/' + str(shout_id),None,False,True)
        response = json.loads(request)
        if "code" in response:
            return None
        else:
            return response["body"]

    def getLastShoutId(self, user_id):
        request = self.httpRequest('shout/user/view/' + str(user_id) + "?trim_user=true",None,False,True)
        response = json.loads(request)
        if "code" in response:
            return None
        else:
            for shout in response:
                if shout["owner"] == str(user_id):
                    return shout["id"]
            return None
            
    def importToKn3(self, url):
        ''' Sube una imagen de un host a kn3 '''
        params = {
                    'url': str(url),
                    'isImage': 1,
                    'key': self.user_key
                    }
        request = self.httpRequest('ajax/shout/attach', params)
        response = json.loads(request)
        if response["status"] == 1:
            return response["data"]["url"]
        else:
            return None

    def httpRequest(self, url, params=None, secure=False, api =None):
        if api is not None:
            baseUrl = 'http://api.taringa.net/'
        else:
            baseUrl = 'http' + ('s' if secure else '') + '://www.taringa.net/'

        baseUrl = baseUrl + url
        try:
            if params is not None:
                request = self.opener.open(baseUrl, urllib.urlencode(params))
            else:
                request = self.opener.open(baseUrl)
            response = request.read()
        except urllib2.HTTPError, e:
            response = e.fp.read()
        return response
