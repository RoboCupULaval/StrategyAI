import math as m
from UltimateStrat.Data.BlackBoard import BlackBoard
from RULEngine.Util.Pose import Pose, Position
from RULEngine.Util.geometry import *
from Util.geometry import *

__author__ = 'RoboCupULaval'


class InfoManager:
    """
    InfoManager is a simple question answerer and setter.
    """
    def __init__(self, field, team, op_team):
        self.black_board = BlackBoard(field, team, op_team)

    def update(self):
        self.black_board.update()

    """ +++ BLACKBOARD +++ """
    # About Game
    # ---Getter
    def getCurrentPlay(self):
        return self.black_board['game']['play']

    def getCurrentPlaySequence(self):
        return self.black_board['game']['sequence']

    # ---Setter
    def setPlay(self, play):
        self.black_board['game']['play'] = play

    # Special stuff
    def initPlaySequence(self):
        self.black_board['game']['sequence'] = 0

    def incPlaySequence(self):
        self.black_board['game']['sequence'] += 1

    def getPrevPlayerPosition(self, i):
        return self.black_board['friend'][str(i - 1)]['position']

    # About Friend player
    # ---Getter
    def getPlayerTarget(self, i):
        return self.black_board['friend'][str(i)]['target']

    def getPlayerGoal(self, i):
        return self.black_board['friend'][str(i)]['goal']

    def getPlayerSkill(self, i):
        return self.black_board['friend'][str(i)]['skill']

    def getPlayerTactic(self, i):
        return self.black_board['friend'][str(i)]['tactic']

    def getPlayerPosition(self, i):
        return self.black_board['friend'][str(i)]['position']

    def getPlayerPose(self, i):
        return self.black_board['friend'][str(i)]['pose']

    def getPlayerOrientation(self, i):
        return self.black_board['friend'][str(i)]['orientation']

    def getPlayerKickState(self, i):
        return self.black_board['friend'][str(i)]['kick']

    def getCountPlayer(self):
        return self.black_board['friend']['count']

    def getPlayerNextAction(self, i):
        return self.black_board['friend'][str(i)]['next_pose']

    # ---Setter
    def setPlayerSkillTargetGoal(self, i, action):
        self.black_board['friend'][str(i)]['skill'] = action['skill']
        self.black_board['friend'][str(i)]['target'] = action['target']
        self.black_board['friend'][str(i)]['goal'] = action['goal']

    def setPlayerTactic(self, i, tactic):
        self.black_board['friend'][str(i)]['tactic'] = tactic

    def setPlayerNextAction(self, i, next_action):
        self.black_board['friend'][str(i)]['next_pose'] = next_action

    # About Ball
    # ---Getter
    def getBallPosition(self):
        return self.black_board['ball']['position']

    """ +++ INTELLIGENCE MODULE +++ """
    # State machine
    # TODO implement getNextState
    def getNextState(self):
        return 'debug'

    # TODO implement getNextPlay
    def getNextPlay(self, state):
        #return 'pQueueLeuLeu'
        return 'pTestBench'

    def getSpeed(self, i):
        list_pose = self.black_board['friend'][str(i)]['retro_pose']

        if not len(list_pose) == 10:
            return {'speed': 0, 'normal': (0, 0), 'vector': (0, 0)}
        else:
            # Get 10 feedback on previous position
            time_ref, pst_ref = list_pose[9]
            time_sec, pst_sec = list_pose[0]

            # Pre calculations
            angle = get_angle(pst_ref.position, pst_sec.position)
            dst_tot = get_distance(pst_ref.position, pst_sec.position)
            time_tot = get_milliseconds(time_ref) - get_milliseconds(time_sec)

            # Final calculations
            speed = dst_tot / time_tot
            normal = (m.cos(m.radians(angle)), m.sin(m.radians(angle)))
            vector = (normal[0] * speed, normal[1] * speed)

            # print('SPEED:{0:.4f} | NORMAL:{1} | VECTOR:{2}'.format(speed, normal, vector))
            return {'speed': speed, 'normal': normal, 'vector': vector}
    def getSpeedBall(self):
        list_pose = self.black_board['ball']['retro_pose']

        if not len(list_pose) == 10:
            return {'speed': 0, 'normal': (0, 0), 'vector': (0, 0)}
        else:
            # Get 10 feedback on previous position
            time_ref, pst_ref = list_pose[9]
            time_sec, pst_sec = list_pose[0]

            # Pre calculations
            angle = get_angle(pst_ref, pst_sec)
            dst_tot = get_distance(pst_ref, pst_sec)
            time_tot = get_milliseconds(time_ref) - get_milliseconds(time_sec)

            # Final calculations
            speed = dst_tot / time_tot
            normal = (m.cos(m.radians(angle)), m.sin(m.radians(angle)))
            vector = (normal[0] * speed, normal[1] * speed)

            # print('SPEED:{0:.4f} | NORMAL:{1} | VECTOR:{2}'.format(speed, normal, vector))
            return {'speed': speed, 'normal': normal, 'vector': vector}