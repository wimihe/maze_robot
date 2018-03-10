#coding:utf-8
#Created by weimi on 2018/2/7.


from src import JsonHandler
from src import AuthJsonHandler
from src.tools import mongo_tool
from src.tools import wx_tool
from src.auth import Auth

from src import utils

class Login(JsonHandler):
    async def post(self):
        code = self.get_body_argument('code')
        encryptedData = self.get_body_argument('encryptedData')
        iv = self.get_body_argument('iv')
        userinfo = wx_tool.get_userinfo(code=code, encryptedData=encryptedData, iv=iv)
        if userinfo:
            session_key = userinfo['session_key']
            openid = userinfo['openid']
            gender = userinfo['gender']
            nickName = userinfo['nickName']
            province = userinfo['province']
            avatarUrl = userinfo['avatarUrl']
            city = userinfo['city']
            user = await utils.init_login(uid=openid, nick=nickName, gender=gender, city=city, photo=avatarUrl,
                                   province=province, session_key=session_key)

            flag, token = Auth.encode_auth_token(uid=user['uid'], secret_key=user['secret_key'])
            if not flag:
                self.write_error_custom(400, 'token error!')
            del user['secret_key']
            user['token'] = token.decode()

            self.write(user)
        else:
            self.write_error_custom(400, '认证失败!')

class FetchMaze(AuthJsonHandler):
    def get(self):
        self.write('success')
