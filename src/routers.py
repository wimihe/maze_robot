#coding:utf-8
#Created by weimi on 2018/2/6.

from src.handlers import api


urls = [
    (r'/login', api.Login),
    (r'/test', api.FetchMaze)
]
