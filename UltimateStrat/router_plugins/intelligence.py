#!/usr/bin/python

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
