#coding:utf-8
'''
  IoT Kit Sender Program v1
  Copyright(C) 2017 ApstoWeb Ltd.
  Cloud Database Connection 1.0
'''
import json, urllib2, cookielib, ssl

def init(userid, password):
  global kvs_server
  ssl._create_default_https_context = ssl._create_unverified_context

  # ユーザ名とパスワードを登録する
  password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
  password_mgr.add_password(None, kvs_server, userid, password)
  auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
  # Cookieを保存する
  cookie_handler = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
  opener = urllib2.build_opener(auth_handler, cookie_handler)
  urllib2.install_opener(opener)


def request(resource, httpmethod, value):
  global kvs_server
  url = kvs_server + resource
  data = json.dumps(value)
  try :
    req = urllib2.Request(url, data)
    req.get_method = lambda: httpmethod
    res = urllib2.urlopen(req)
    response = json.loads(res.read())
  except urllib2.HTTPError as e:
    response = json.loads(e.read())
  return response

