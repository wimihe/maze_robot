#coding:utf-8
#Created by weimi on 2018/2/6.

import tornado.web
from bson.json_util import dumps

from src.utils import fetch_secret_key
from src.auth import Auth

class BaseHandler(tornado.web.RequestHandler):

    def db(self):
        return self.application.db


class JsonHandler(BaseHandler):

    def write(self, chunk):
        if isinstance(chunk, (list, tuple)):
            chunk = {
                'total': len(chunk),
                'data': chunk
            }

        self.set_header('Content-Type', 'application/json')
        chunk = {
            'statusCode': 200,
            'errorMessage': 'success',
            'data': chunk
        }
        super(BaseHandler, self).write(dumps(chunk))

    def write_error_custom(self, status_code, reason):
        data = {'statusCode': status_code, 'errorMessage': reason}
        self.set_status(status_code=status_code, reason=reason)
        self.write(data)

class AuthJsonHandler(JsonHandler):

    async def prepare(self):
        super(AuthJsonHandler, self).prepare()
        token = self.request.headers.get('Authorization', None)
        uid = self.request.headers.get('access-token', None)
        flag, secret_key = await fetch_secret_key(uid=uid)
        if not flag:
            self.write_error_custom(403, secret_key)
            return False
        flag, data = Auth.decode_auth_token(auth_token=token, secret_key=secret_key)
        if not flag:
            self.write_error_custom(403, data)
            return False
        setattr(self, '_current_user', uid)
