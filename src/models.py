#coding:utf-8
#Created by weimi on 2018/3/9.

# from

import re
import datetime

class BaseField(object):

    def __init__(self, require=False):
        self.require = require
        self.type = None

    def validate(self, value):
        if self.type != None:
            if not isinstance(value, self.type):
                raise ValueError('属性类型必须为:%s' % (str(self.type)))

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

    db = None

    @classmethod
    def filter(cls, **kwargs):
        pass

    def __init__(self, **kwargs):
        self._id = None
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def _field_dict(self):
        return {}

    def _field_list(self):
        return []

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
                data[key] = getattr(self, key)
                field.validate(data[key])

    def save(self, update_fields=None):
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

        self._save(params=self._get_save_data(keys=keys))

    def _add(self, data):
        # data =
        # self._id = data['_id']
        pass

    def _update(self, data):
        pass

    def _save(self, params):
        if not params:
            return
        if self._is_create():
            self._add(params)

        else:
            self._update(params)

    class Meta:
        db_table = None

# class User(object):


import pdb;pdb.set_trace()