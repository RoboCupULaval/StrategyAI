from UltimateStrat.Data.BlackBoard import BlackBoard

__author__ = 'jbecirovski'


class InfoManager:
    """
    InfoManager is a simple question answerer and setter.
    """
    def __init__(self, field, team, op_team):
        self.black_board = BlackBoard(field, team, op_team)

    """ +++ BLACKBOARD +++ """
    # About Game
    # Getter
    def getCurrentPlay(self):
        return self.black_board['game']['play']

    def getCurrentPlaySequence(self):
        return self.black_board['game']['sequence']

    # Setter
    def setPlay(self, play):
        self.black_board['game']['play'] = play

    # Special stuff
    def initPlaySequence(self):
        self.black_board['game']['sequence'] = 0

    def incPlaySequence(self):
        self.black_board['game']['sequence'] += 1

    def getPrevBotPosition(self, i):
        return self.black_board['friend'][str(i - 1)]['position']

    # About Friend player
    # Getter
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

    # Setter
    def setPlayerSkillTargetGoal(self, i, action):
        self.black_board['friend'][str(i)]['skill'] = action['skill']
        self.black_board['friend'][str(i)]['target'] = action['target']
        self.black_board['friend'][str(i)]['goal'] = action['goal']

    def setPlayerTactic(self, i, tactic):
        self.black_board['friend'][str(i)]['tactic'] = tactic

    def setPlayerNextPose(self, i, next_pose):
        self.black_board['friend'][str(i)]['next_pose'] = next_pose

    # About Ball
    ### Getter
    def getBallPosition(self):
        return self.black_board['ball']['position']

    """ +++ INTELLIGENCE MODULE +++ """
    # State machine
    # TODO implement getNextState
    def getNextState(self):
        return 'debug'

    # TODO implement getNextPlay
    def getNextPlay(self, state):
        return 'pQueueLeuLeu'
