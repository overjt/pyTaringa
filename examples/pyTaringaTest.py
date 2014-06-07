# -*- coding: utf-8 -*-
import time
from pyTaringa import pyTaringa

if __name__ == '__main__':
    username = "YOUR USERNAME"
    password = "YOUR PASSWORD"
    taringa = pyTaringa(username,password)
    print taringa.username
    print taringa.password
    print taringa.user_key
    print taringa.user_id
    print taringa.cookie
    print taringa.shoutText("#Test - PyT")
    time.sleep(8)
    print taringa.shoutImage("#Test - PyT - ImageShout","http://traduccionesyedra.files.wordpress.com/2012/04/testing.jpg")
    print taringa.getUserId("anpep")
    print taringa.getUserId("overjt")
    print taringa.likeShout("47574275","19963011")
    print taringa.deleteShout("47405007")
    print taringa.getShoutText("47420358")
    lastShout = taringa.getLastShoutId("19963011")
    print lastShout
    print taringa.getShoutText(lastShout)
    print taringa.importToKn3("http://www.rafaelrojas.net/wp-content/uploads/2012/03/Arch-Linux.png")
