from RULEngine.Util.area import isInsideSquare, isInsideCircle
from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from Util.geometry import *
from math import *

__author__ = 'Yassine'


class tIntercept(TacticBase):
    def __init__(self):
        TacticBase.__init__(self, self.__class__.__name__)

    def apply(self, info_manager, id_player):
        # Global variables
        # y_max = 2000
        straf = -3500
        minimal_ball_speed = 0.5
        initial_position = Position(straf, 0)

        # Finding the ball trajectory
        ball_speed = info_manager.getSpeedBall()
        ball_position = info_manager.getBallPosition()
        ball_position_prediction = Position(ball_speed['vector'][0], ball_speed['vector'][1]) + ball_position
        ball_vector = (ball_position, ball_position_prediction)

        # Intercept the ball while staying on the same line
        # bot_vector = (Position(straf, -y_max), Position(straf, y_max))
        # interseption_point = get_intersection(bot_vector, ball_vector)

        # Intercept the ball while finding the shortest path to the ball trajectory
        bot_position = info_manager.getPlayerPosition(id_player)
        interseption_point = get_intersection(get_orthogonal(ball_position_prediction, bot_position), ball_vector)

        # if isInsideCircle(interseption_point, initial_position, 2000) and ball_speed['speed'] > minimal_ball_speed:
        #     # if the bot can catch the ball, he goes for it
        #     return {'skill': 'sFaceTarget', 'target': interseption_point, 'goal': ball_vector}
        # else:
        #     # or he goes to his original position
        #     return {'skill': 'sFaceTarget', 'target': initial_position, 'goal': ball_position}

        if ball_speed['speed'] > minimal_ball_speed:
            # if the bot can catch the ball, he goes for it
            return {'skill': 'sFaceTarget', 'target': interseption_point, 'goal': ball_vector}
        else:
            # or he goes to his original position
            return {'skill': 'sFaceTarget', 'target': initial_position, 'goal': ball_position}