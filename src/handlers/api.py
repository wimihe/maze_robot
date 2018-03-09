#coding:utf-8
#Created by weimi on 2018/2/7.


from src import JsonHandler
from src import AuthJsonHandler
from src.tools import mongo_tool
from src.tools import wx_tool

from src import utils

class Login(AuthJsonHandler):
    async def post(self):
        print('----')
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
            user = utils.init_user(uid=openid, nick=nickName, gender=gender, city=city, photo=avatarUrl,
                                   province=province, session_key=session_key)
            self.write(user)
        print(userinfo)
        self.write(userinfo)

class FetchMaze(JsonHandler):
    def get(self):
        pass
