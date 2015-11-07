#import sys
#sys.path.append(".")
from RULEngine.Framework import start_game
from UltimateStrategy import UltimateStrategy

__author__ = 'jbecirovski'

if __name__ == '__main__':
    start_game(UltimateStrategy, serial=True)

