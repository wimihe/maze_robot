#coding:utf-8
#Created by weimi on 2018/2/6.


MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = None
MONGODB_DB_NAME = 'maze_robot'

APPID = ''
APPSECRET = ''

try:
    from src.local_settings import *
except Exception as e:
    print(e)