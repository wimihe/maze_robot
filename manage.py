#coding:utf-8
#Created by weimi on 2018/3/8.


from tornado.ioloop import IOLoop

from src.application import MazeRobot

app = MazeRobot()
app.listen(8888)
IOLoop.current().start()

