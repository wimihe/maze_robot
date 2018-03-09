#coding:utf-8
#Created by weimi on 2018/2/6.

import tornado.web

import motor.motor_tornado

from src import settings
from src import routers
from src import utils
from src.models import BaseModel

class MazeRobot(tornado.web.Application):

    def __init__(self):
        self.db = motor.motor_tornado.MotorClient(**utils.fetch_mongodb_for_motor(settings=settings))[settings.MONGODB_DB_NAME]
        BaseModel.db = self.db
        super(MazeRobot, self).__init__(routers.urls)
