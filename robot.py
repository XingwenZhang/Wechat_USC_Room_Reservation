# coding : utf-8

from werobot import WeRoBot 

robot = WeRoBot(token = 'angus')

@robot.handler
def hello(message):
	return 'Hello World'