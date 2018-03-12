#coding:utf-8
#Created by weimi on 2018/2/7.


from src import JsonHandler
from src import AuthJsonHandler
from src.tools import wx_tool
from src.auth import Auth

from src import utils
from src import models

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

class Maze(AuthJsonHandler):
    async def get(self):

        maze_id = self.get_argument('maze_id')

        flag, maze = await models.Maze.fetch(uid=self.current_user, maze_id=maze_id)
        if flag:
            self.write(maze)
        else:
            self.write_error_custom(404, maze)

    async def post(self):

        maze_id = self.get_body_argument('maze_id')
        path = self.get_body_argument('path')
        block_list = self.get_body_argument('block_list')

        flag, data = await models.Resolve.resolve(maze_id=maze_id, uid=self.current_user, path=path, block_list=block_list)

        if flag:
            self.write(data)
        else:
            self.write_error_custom(400, data)

class MazeList(AuthJsonHandler):
    async def get(self):

        result = await models.Maze.list()

        self.write(result)

class Ranklist(AuthJsonHandler):
    async def get(self):
        maze_id = self.get_argument('maze_id')
        result = await models.Resolve.ranklist(maze_id=maze_id, top=50)
        self.write(result)