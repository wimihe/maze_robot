#coding:utf-8
#Created by weimi on 2018/3/9.


import requests

def post(url, data=None, json=None, **kwargs):
    res = requests.post(url=url,data=data, json=json, **kwargs)
    return res

def get(url, params=None, **kwargs):
    res = requests.get(url=url,params=params, **kwargs)
    return res

def request(method, url, **kwargs):
    res = requests.request(method=method, url=url, **kwargs)
    return res