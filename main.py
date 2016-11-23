# Under MIT License, see LICENSE.txt
""" Point d'entrée de l'intelligence artificielle. """
from RULEngine.Framework import Framework
from coach import Coach

__author__ = 'RoboCupULaval'

if __name__ == '__main__':
    ai_coach = Coach()
    Framework().start_game(ai_coach.main_loop, ai_coach.set_team_color)
