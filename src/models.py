#coding:utf-8
#Created by weimi on 2018/3/9.

from src.tools.models_tool import *

class User(BaseModel):

    uid = TextField(require=True)
    nick = TextField(require=True)
    gender = IntField(require=True)
    photo = TextField(require=True)
    province = TextField(require=False)
    city = TextField(require=False)
    secret_key = TextField(require=True)
    ctime = DatetimeField(require=True, auto_now_add=True)
    mtime = DatetimeField(require=True, auto_now=True)

    class Meta:
        db_table = 'User'

    def to_dict(self, detail=False):
        data = super(User, self).to_dict()
        if detail == False and 'secret_key' in data:
            del data['secret_key']
        return data

    @classmethod
    def user2Simple(cls, user):
        keys = ['uid', 'nick', 'gender', 'photo']
        for key in user.keys():
            if key not in keys:
                del user[key]
        return user

    @classmethod
    async def get(cls, uid):
        data = await cls.find_one({'uid': uid})
        if data:
            return True, data
        return False, 'not found'

class Maze(BaseModel):

    name = TextField(require=True)
    maze = ArrayField(require=True)
    ctime = DatetimeField(require=True, auto_now_add=True)
    mtime = DatetimeField(require=True, auto_now=True)

    class Meta:
        db_table = 'Maze'

    @classmethod
    async def list(cls):
        total, data = await cls.find(sort={'ctime': 1})
        return {
            'total': total,
            'list': data
        }

    @classmethod
    async def fetch(cls, uid, maze_id):
        flag, maze = await cls.get(maze_id=maze_id)
        if not flag:
            return False, maze
        await MazeResolveInit.update_init(maze_id=maze_id, uid=uid)
        return True, maze

    @classmethod
    async def get(cls, maze_id):
        maze = await cls.find_one({'_id': cls.id2ObjectId(maze_id)})
        if not maze:
            return False, 'maze not found'
        return True, maze

class MazeResolveInit(BaseModel):

    maze_id = TextField(require=True)
    uid = TextField(require=True)
    ctime = DatetimeField(require=True, auto_now_add=True)
    mtime = DatetimeField(require=True, auto_now=True)
    timestamp = FloatField(require=True)

    class Meta:
        db_table = 'MazeResolveInit'

    @classmethod
    async def get(cls, maze_id, uid):
        data = await cls.find_one({'maze_id': str(maze_id), 'uid': uid})
        if data:
            return True, data
        return False, 'not found'

    @classmethod
    async def update_init(cls, maze_id, uid):
        flag, data = await cls.get(maze_id=maze_id, uid=uid)
        timestamp = datetime.datetime.now().timestamp()
        if not flag:
            m = cls()
            m.maze_id = maze_id
            m.uid = uid
            m.timestamp = timestamp
        else:
            m = MazeResolveInit(**data)
            m.timestamp = timestamp
        await m.save(update_fields=['timestamp', 'mtime'])
        return True

    @classmethod
    async def get_init_timestamp(cls, maze_id, uid):
        flag, data = await cls.get(maze_id=maze_id, uid=uid)
        if not flag:
            return False, -1
        return True, data['timestamp']

class Resolve(BaseModel):

    maze_id = TextField(require=True)
    uid = TextField(require=True)
    user = DictField(require=True)
    path = ArrayField(require=True)
    block_list = ArrayField(require=True)
    step = IntField(require=True)
    ctime = DatetimeField(require=True, auto_now_add=True)
    mtime = DatetimeField(require=True, auto_now=True)
    duration = FloatField(require=True)

    class Meta:
        db_table = 'Resolve'

    @classmethod
    async def get(cls, maze_id, uid):
        data = await cls.find_one({'maze_id': maze_id, 'uid': uid})
        if not data:
            return False, 'not found'
        return True, data

    @classmethod
    async def resolve(cls, maze_id, uid, path, block_list):
        timestamp = datetime.datetime.now().timestamp()
        flag, start_timestamp = await MazeResolveInit.get_init_timestamp(maze_id=maze_id, uid=uid)
        if not flag:
            return False, 'error'

        flag, user = User.get(uid=uid)

        if not flag:
            return False, 'error'

        flag, maze = await Maze.get(maze_id=maze_id)

        if not flag:
            return False, maze

        from src.tools import maze_tool
        flag, step = maze_tool.validate_maze_path(path=path, block_list=block_list, maze=maze['maze'])
        if not flag:
            return False, step

        duration = timestamp - start_timestamp

        flag, m = cls.get(maze_id=maze_id, uid=uid)
        if flag == True:
            if (m['step'] < step) or (m['step'] == step and m['duration'] <= duration):
                return True, {
                    'record': False,
                    'step': m['step'],
                    'duration': m['duration'],
                }
            m = cls(**m)
        else:
            m = cls()
            m.maze_id = maze_id
            m.uid = uid
        m.user = User.user2Simple(user)
        m.path = path
        m.block_list = block_list
        m.step = step
        m.duration = duration
        await m.save()
        return True, {
            'record': True,
            'step': step,
            'duration': duration
        }

    @classmethod
    async def ranklist(cls, maze_id, top=50):

        total, result = await cls.find(filter={'maze_id': maze_id}, sort=[('step', 1), ('mtime', 1), ('duration', 1)],
                        fields={'user': 1, 'step': 1, 'duration': 1, 'mtime': 1}, page=1, page_size=top)

        return result



