#coding:utf-8
#Created by weimi on 2018/3/9.

# from

import re
import datetime
from bson import ObjectId

from src.tools import mongo_tool

class BaseField(object):

    def __init__(self, require=False):
        self.require = require
        self.type = None

    def validate(self, value):
        if self.type != None:
            if not isinstance(value, self.type):
                raise ValueError('属性类型必须为:%s 当前为%s' % (str(self.type), type(value)))

class TextField(BaseField):

    def __init__(self, require=False, max_length=None, regex=None):
        super(TextField, self).__init__(require=require)

        self.max_length = max_length
        self.regex = regex
        self.type = str

    def validate(self, value):
        super(TextField, self).validate(value)
        if self.max_length != None:
            if len(value) > self.max_length:
                raise ValueError('长度不得大于:%d' % (self.max_length))

        if self.regex != None:
            if not re.search(self.regex, value):
                raise ValueError('与正则不匹配:%s' % (self.regex))

class IntField(BaseField):

    def __init__(self, require=False, min=None, max=None):
        super(IntField, self).__init__(require=require)
        self.min = min
        self.max = max
        self.type = int

    def validate(self, value):
        super(IntField, self).validate(value)
        if self.min != None:
            if value < self.min:
                raise ValueError('值不得小于:%d' % self.min)
        if self.max != None:
            if value > self.max:
                raise ValueError('值不得大于:%d' % self.max)

class FloatField(BaseField):

    def __init__(self, require=False):
        super(FloatField, self).__init__(require=require)
        self.type = float

class EnumField(BaseField):

    def __init__(self, choices, require=False):
        super(EnumField, self).__init__(require=require)
        self.choices = choices

    def validate(self, value):
        super(EnumField, self).validate(value)
        if value not in self.choices:
            raise ValueError('值不在候选项里:' % str(self.choices))

class ArrayField(BaseField):

    def __init__(self, require=False, max_length=None):
        super(ArrayField, self).__init__(require=require)
        self.type = (list, tuple)
        self.max_length = max_length

    def validate(self, value):
        super(ArrayField, self).validate(value)
        if self.max_length != None:
            if len(value) > self.max_length:
                raise ValueError('长度不得大于:%d' % (self.max_length))

class DictField(BaseField):

    def __init__(self, require=False):
        super(DictField, self).__init__(require=require)
        self.type = dict

class DateField(BaseField):

    def __init__(self, require=False, auto_now_add=False, auto_now=False):
        super(DateField, self).__init__(require=require)
        self.type = datetime.date
        self.auto_now_add = auto_now_add
        self.auto_now = auto_now

    def now(self):
        return self.type.today()

class DatetimeField(BaseField):

    def __init__(self, require=False, auto_now_add=False, auto_now=False):
        super(DatetimeField, self).__init__(require=require)
        self.type = datetime.datetime
        self.auto_now_add = auto_now_add
        self.auto_now = auto_now

    def now(self):
        return self.type.now()

class BaseModel(object):

    _db = None

    @classmethod
    def __field_list__(cls):
        field_list = getattr(cls, '__field_list', None)
        if field_list == None:
            field_list = []
            for i in dir(cls):
                field = getattr(cls, i)
                if isinstance(field, BaseField):
                    field_list.append({'id': i, 'field': field})
            setattr(cls, '__field_list', field_list)
        return field_list

    @classmethod
    def __filed_dict__(cls):
        filed_dict = getattr(cls, '__filed_dict', None)
        if filed_dict == None:
            attr_list = cls.__field_list__()
            filed_dict = {}
            for item in attr_list:
                filed_dict[item['id']] = item['field']
            setattr(cls, '__filed_dict', filed_dict)
        return filed_dict

    @classmethod
    def id2ObjectId(cls, _id):
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        return _id

    @classmethod
    def db(cls):
        return cls._db[cls.Meta.db_table]

    @classmethod
    async def find(cls, filter=None, sort=None, fields=None, page=1, page_size=3000):
        return await mongo_tool.find(db=cls.db(), filter=filter, sort=sort, fields=fields, page=page, page_size=page_size)

    @classmethod
    async def find_one(cls, filter):
        return await mongo_tool.find_one(db=cls.db(), filter=filter)

    def __init__(self, **kwargs):

        self._id = None

        for key in self.__class__.__filed_dict__().keys():
            setattr(self, key, None)
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def to_dict(self):
        keys = self._field_dict().keys()
        result = {}
        for key in keys:
            if hasattr(self, key):
                result[key] = getattr(self, key)
        return result

    def _field_dict(self):
        return self.__class__.__filed_dict__()

    def _field_list(self):
        return self.__class__.__field_list__()

    def _is_create(self):
        return self._id == None

    def _get_save_data(self, keys):

        fields_dict = self._field_dict()
        is_create = self._is_create()
        for key in fields_dict.keys():
            if key in keys:
                continue
            field = fields_dict[key]
            if isinstance(field, (DatetimeField, DateField)):
                if (is_create and field.auto_now_add) or field.auto_now:
                    keys.append(key)
            elif is_create and field.require == True:
                keys.append(key)
        data = {}
        for key in keys:
            field = fields_dict[key]
            if isinstance(field, (DateField, DatetimeField)):
                if (is_create and field.auto_now_add) or field.auto_now:
                    data[key] = field.now()
                    setattr(self, key, data[key])
                    continue

            if not hasattr(self, key):
                if field.require == True:
                    raise ValueError('字段%s是必填的' % key)
            else:
                value = getattr(self, key)
                if value == None:
                    if field.require == True:
                        raise ValueError('字段%s是必填的' % key)
                    continue
                data[key] = value
                try:
                    field.validate(data[key])
                except Exception as e:
                    raise ValueError('%s: %s' % (key, str(e)))
        return data

    async def save(self, update_fields=None):
        if not self._is_create() and update_fields:
            update_fields = list(set(update_fields))
            field_dict = self._field_dict()
            keys = []
            for key in update_fields:
                if key not in field_dict:
                    raise ValueError('无此字段:%s' % key)
                keys.append(key)

        else:
            keys = list(self._field_dict().keys())
        await self._save(params=self._get_save_data(keys=keys))

    async def _add(self, data):
        self._id = await mongo_tool.insert(db=self.__db__(), data=data)

    async def _update(self, data):
        await mongo_tool.update(db=self.__db__(), filter={'_id': self._id}, data=data)

    async def _save(self, params):
        if not params:
            return
        if self._is_create():
            await self._add(params)

        else:
            await self._update(params)

    def __db__(self):
        return self.__class__.db()

    class Meta:
        db_table = None

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



