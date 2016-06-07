#Under MIT License, see LICENSE.txt
# TODO: Implementer l'algorithme de pathfinding et rendre générique pour cette fonction
from ai.Executor.Executor import Executor
from ai.InfoManager import InfoManager
import random
import math

__author__ = 'agingrasc'

class PathfinderExecutor:
    """
    PathfinderExecutor est une serie d'iteration pour trouver le prochain
    point de deplacement de chaque joueur avec un RapidRandomTree pathfinder.

    1 - Quel est la position actuel du joueur?
    2 - Quel est son objectif?
    3 - Generation du mouvement a effectuer.
        S3 - Validation de chaque delta contre les contraintes.
    """
    def __init__(self, InfoManager):
        Executor.__init__(self, InfoManager)
        self.rrt = []

    def exec(self):
        # Fonction vide pour faire marcher le test
        for i in range(InfoManager.getCountPlayer()):
            None


    def gen_rrt(player):
        """Prend un joueur et genere son rrt pour trouver un chemin"""

        # 1 - Position du joueur
        pos = InfoManager.getPlayerPosition(player)
        # 2 - Cible
        target = InfoManager.getPlayerTarget(player)

        # 3 - Generation
        # rrt doit etre implemente


    def is_near(target, latest):
        # Fonction vide pour faire marcher le test
        None

    def norm(pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
