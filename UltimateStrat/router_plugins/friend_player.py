#!/usr/bin/python

import Router

# About Friend player
# ---Getter
@Router.register_function
def getPlayerTarget(i):
    return Router.black_board['friend'][str(i)]['target']

@Router.register_function
def getPlayerGoal(i):
    return Router.black_board['friend'][str(i)]['goal']

@Router.register_function
def getPlayerSkill(i):
    return Router.black_board['friend'][str(i)]['skill']

@Router.register_function
def getPlayerTactic(i):
    return Router.black_board['friend'][str(i)]['tactic']

@Router.register_function
def getPlayerPosition(i):
    return Router.black_board['friend'][str(i)]['position']

@Router.register_function
def getPlayerPose(i):
    return Router.black_board['friend'][str(i)]['pose']

@Router.register_function
def getPlayerOrientation(i):
    return Router.black_board['friend'][str(i)]['orientation']

@Router.register_function
def getPlayerKickState(i):
    return Router.black_board['friend'][str(i)]['kick']

@Router.register_function
def getCountPlayer():
    return Router.black_board['friend']['count']

@Router.register_function
def getPlayerNextPose(i):
    return Router.black_board['friend'][str(i)]['next_pose']

# ---Setter
@Router.register_function
def setPlayerSkillTargetGoal(i, action):
    Router.black_board['friend'][str(i)]['skill'] = action['skill']
    Router.black_board['friend'][str(i)]['target'] = action['target']
    Router.black_board['friend'][str(i)]['goal'] = action['goal']

@Router.register_function
def setPlayerTactic(i, tactic):
    Router.black_board['friend'][str(i)]['tactic'] = tactic

@Router.register_function
def setPlayerNextPose(i, next_pose):
    Router.black_board['friend'][str(i)]['next_pose'] = next_pose

@Router.register_function
def getSpeed(i):
    return Router.black_board['friend'][str(i)]['speed']
