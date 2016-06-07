# Under MIT License, see LICENSE.txt
from AI.STP.Tactic.TacticBase import TacticBase
from AI.Util.geometry import distance
from RULEngine.Util.Position import Position

__author__ = 'RoboCupULaval'


class tKickerTest(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        bot_pst = info_manager.getPlayerPosition(id_player)
        ball_pst = info_manager.getBallPosition()

        if distance(Position(), ball_pst) < 500:
            if distance(bot_pst, ball_pst) < 180:
                return {'skill': 'sKickMedium', 'target': bot_pst, 'goal': bot_pst}
            else:
                return {'skill': 'sFollowTarget', 'target': ball_pst, 'goal': bot_pst}
        else:
            return {'skill': 'sFollowTarget', 'target': Position(1000, 0), 'goal': bot_pst}
