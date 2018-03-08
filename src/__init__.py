#coding:utf-8
#Created by weimi on 2018/2/6.

import tornado.web
from bson.json_util import dumps

class BaseHandler(tornado.web.RequestHandler):

    def db(self):
        return self.application.db['dev4db_develop']


class JsonHandler(BaseHandler):

    def write(self, chunk):
        if isinstance(chunk, (list, tuple)):
            chunk = {
                'total': len(chunk),
                'data': chunk
            }

        self.set_header('Content-Type', 'application/json')

        super(BaseHandler, self).write(dumps(chunk))