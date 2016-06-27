# Under MIT License, see LICENSE.txt
""" Point d'entrée de l'intelligence artificielle. """
from RULEngine.Framework import Framework
from Coach import Coach 

__author__ = 'RoboCupULaval'

if __name__ == '__main__':
    Framework().start_game(Coach)
