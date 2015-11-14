#!/usr/bin/python

import Router

# About Game
# ---Getter
@Router.register_function
def getCurrentPlay():
    return Router.black_board['game']['play']

@Router.register_function
def getCurrentPlaySequence():
    return Router.black_board['game']['sequence']

# ---Setter
@Router.register_function
def setPlay(play):
    Router.black_board['game']['play'] = play

# Special stuff
@Router.register_function
def initPlaySequence():
    Router.black_board['game']['sequence'] = 0

@Router.register_function
def incPlaySequence():
    Router.black_board['game']['sequence'] += 1

@Router.register_function
def getPrevPlayerPosition(i):
    return Router.black_board['friend'][str(i - 1)]['position']
