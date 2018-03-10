#coding:utf-8
#Created by weimi on 2018/2/6.

from src import constants
from src import models


def fetch_settings_val(settings, key, default=None):
    return getattr(settings, key, default)


def fetch_mongodb_for_motor(settings):
    return {
        'host': fetch_settings_val(settings=settings, key=constants.MONGODB_HOST_KEY, default='127.0.0.1'),
        'port': fetch_settings_val(settings=settings, key=constants.MONGODB_PORT_KEY, default=None),
    }

async def init_login(uid, nick, gender, city, photo, province, session_key):

    user = await models.User.find_one({'uid': uid})
    if not user:
        print('create')
        data = dict(
            uid=uid,
            nick=nick,
            gender=gender,
            city=city,
            photo=photo,
            province=province,
            secret_key=session_key
        )
        user = models.User(**data)
        await user.save()
    else:
        print('update')
        user = models.User(**user)
        await user.save()

    return user.to_dict()