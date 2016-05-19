#!/usr/bin/python

from UltimateStrat.Module.geometry import *
import Router

# State machine
# TODO implement getNextState
@Router.register_function
def getNextState():
    return 'debug'

# TODO implement getNextPlay
@Router.register_function
def getNextPlay(state):
    return Router.getCurrentPlay()

@Router.register_function
def getSpeedBall():
    return getDictSpeed(Router.black_board['ball']['retro_pose'])

@Router.register_function
def getPlayerSpeed(i):
    return getDictSpeed(Router.black_board['friend'][str(i)]['retro_pose'])
