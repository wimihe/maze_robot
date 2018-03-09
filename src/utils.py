#coding:utf-8
#Created by weimi on 2018/2/6.

from src import constants


def fetch_settings_val(settings, key, default=None):
    return getattr(settings, key, default)


def fetch_mongodb_for_motor(settings):
    return {
        'host': fetch_settings_val(settings=settings, key=constants.MONGODB_HOST_KEY, default='127.0.0.1'),
        'port': fetch_settings_val(settings=settings, key=constants.MONGODB_PORT_KEY, default=None),
    }

def init_user(uid, nick, gender, city, photo, province, session_key):

    flag, user = models.User.add_user(uid=uid, nick=nick, gender=gender,
                                      city=city, photo=photo, province=province,
                                      access_token=access_token)
    if flag == False:
        raise ValueError('登录失败')
    return models.User.to_dict(user=user, base=False, access_token=True)