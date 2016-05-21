# TODO: renommer PathfinderExecutor et rendre générique pour cette fonction
from UltimateStrat.Executor.Executor import Executor
from PythonFramework.Util.constant import *
from StrategyIA.Util.rrt import Tree
import random
import math

__author__ = 'agingrasc'

class RRTExecutor:
    """
    RRTExecutor est une serie d'iteration pour trouver le prochain point de
    deplacement de chaque joueur avec un RapidRandomTree pathfinder.
    1 - Quel est la position actuel du joueur?
    2 - Quel est son objectif?
    3 - Generation du mouvement a effectuer.
        S3 - Validation de chaque delta contre les contraintes.
    """
    def __init__(self, info_manager):
        Executor.__init__(self, info_manager)
        self.rrt = []

    def exec(self):
        for i in range(info_manager.getCountPlayer()):
            gen_rrt(i)

    """ Prend un joueur et genere son rrt pour trouver un chemin """
    def gen_rrt(i):
        # 1 - Position?
        pos = info_manager.getPlayerPosition(i)
        # 2 - Objectif positionnel?
        target = info_manager.getPlayerTarget(i)

        # 3 - Generation
        # rrt doit etre implemente
        lrrt = Tree(pos)
        latest = (-9999, -9999)
        rand_gen = random.random();
        while(not near(target, latest)):
            rand_pos = rand_gen.randint(FIELD_X_LEFT, FIELD_X_RIGHT), rand_gen.randint(FIELD_Y_BOTTOM, FIELD_Y_TOP)
            nearest = lrrt.find_nearest(rand_pos)

    def is_near(target, latest):

    def norm(pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
