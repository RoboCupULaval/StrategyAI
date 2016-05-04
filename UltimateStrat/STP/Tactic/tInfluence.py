from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from Util.geometry import *
import math as m
from RULEngine.Util.geometry import get_angle
from RULEngine.Util.Pose import Pose, Position

__author__ = 'yassinez'


class tInfluence(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        bot_position = info_manager.getPlayerPose(id_player).position
        ball_position= info_manager.getBallPosition()
        dst_ball_bot = distance(ball_position, bot_position)
        theta = get_angle(bot_position,ball_position)
        #x= bot_position.x + m.cos(theta)*V
        #y= bot_position.y + m.sin(theta)*V
        #point_relatif = info_manager.getPlayerPose(info_manager.getPlayerPosition(x,y),info_manager.getPlayerOrientation())
        pos_Obstacle = []
        for i in range(0,6):
            if not (i == id_player):
                pos_Obstacle.append(info_manager.getPlayerPosition(i))

        if dst_ball_bot > 10:
            ###code à mettre
            vec_rel= Position(bot_position.x+m.cos(theta)*100, bot_position.y+m.sin(theta)*100)

            for position in pos_Obstacle:
                angle= get_angle(bot_position,position)
                R=distance(bot_position,position)
                if R == 0.0:
                    R = 0.01
                V=(-1000000/(R))
                vec_obs = Position(m.cos(angle)*V, m.sin(angle)*V)
                vec_rel += vec_obs
                #print(vec_obs)
                #print(vec_rel)
            n=m.atan2(vec_rel.y-bot_position.y,vec_rel.x-bot_position.x)
            vec=Position(bot_position.x+m.cos(n)*1000, bot_position.y+m.sin(n)*1000)

            return {'skill': 'sFollowTarget', 'target':vec, 'goal': ball_position}
        else:
            print('STOP BITCH')
            return {'skill': 'sStop', 'target': bot_position, 'goal': bot_position}