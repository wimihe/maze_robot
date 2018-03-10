#coding:utf-8
#Created by weimi on 2018/3/10.

import jwt
import datetime

class Auth(object):

    @staticmethod
    def encode_auth_token(uid, secret_key):

        try:
            payload = {
                'id': uid,
                'login_time': datetime.datetime.now().timestamp()
            }
            return True, jwt.encode(
                payload,
                secret_key,
                algorithm='HS256'
            )
        except Exception as e:
            return False, e

    @staticmethod
    def decode_auth_token(auth_token, secret_key):

        try:
            payload = jwt.decode(auth_token, secret_key, options={'verify_exp': False})
            if ('id' in payload and 'login_time' in payload):
                return True, payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return False, 'Token过期'
        except jwt.InvalidTokenError:
            return False, '无效Token'
