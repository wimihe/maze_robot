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