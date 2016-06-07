# Under MIT License, see LICENSE.txt
from RULEngine.Util.Position import Position
from AI.STP.Tactic.TacticBase import TacticBase
from AI.Util.geometry import distance

__author__ = 'RoboCupULaval'


class tTestBench(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        bot_pst = info_manager.get_player_position(id_player)
        ball_pst = info_manager.get_ball_position()
        action = info_manager.get_player_next_action(id_player)

        ### PATH and KICK :: TestBench ###
        if distance(Position(), ball_pst) < 300:
            if distance(bot_pst, ball_pst) < 180:
                return {'skill': 'sKickHigh', 'target': bot_pst, 'goal': bot_pst}
            else:
                return {'skill': 'sFollowTarget', 'target': ball_pst, 'goal': bot_pst}
        else:
            if isinstance(action, list):
                return {'skill': 'sWait', 'target': bot_pst, 'goal': bot_pst}
            else:
                return {'skill': 'sGeneratePath', 'target': bot_pst, 'goal': bot_pst}
