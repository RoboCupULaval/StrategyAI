from UltimateStrat.Executor.Executor import Executor
from PythonFramework.Util.constant import *
import random

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
        lrrt = Rrt(pos)
        latest = (-9999, -9999)
        rand_gen = random.random();
        while(not near(target, latest)):
            rand_pos = rand_gen.randint(FIELD_X_LEFT, FIELD_X_RIGHT), rand_gen.randint(FIELD_Y_BOTTOM, FIELD_Y_TOP)
            nearest = lrrt.nearest(rand_pos)
