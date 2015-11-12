from UltimateStrat.Executor.Executor import Executor
from PythonFramework.Util.constant import *
from PythonFramework.Util.Position import Position
import math

ROBOT_RADIUS = 300

class PFAxisExecutor(Executor):
    """
    PFAxisExecutor (PathFinder Axis) est une sequence de requetes permettant
    de fournir le pathfinder pour un seul robot qui cherche a se positionner
    pour kick la balle.
    1 - Ou est le robot?
    2 - Quelle est l'orientation du robot?
    3 - Ou est la balle?
    4 - Quel chemin doit-il emprunter pour avoir le dribbler sur la balle?
    """
    def __init__(self, info_manager):
        Executor.__init__(self, info_manager)
        self.pose = Position(0, 0)
        self.orientation = 0
        self.target = Position(-99999, -99999)
        self.paths = []

    def exec(self):
        # 1 Ou est le robot
        self.pose = self.info_manager.getPlayerPosition(0)

        # 2 Quelle est l'orientation
        self.orientation = self.info_manager.getPlayerPose(0)

        # 3 Position de la target
        self.target = self.info_manager.getPlayerTarget(0)

        # 4 Chemin a emprunter

    def is_ball_x(self):
        kx_max = math.ceil((FIELD_X_RIGHT - self.pose.x)/math.cos(self.orientation)) + 1
        kx_min = math.floor((FIELD_X_LEFT - self.pose.x)/math.cos(self.orientation))

        for i in range(kx_min, kx_max):
            tx = math.floor(i*math.cos(self.orientation) + self.pose.x)
            if tx == self.target.x:
                ty = math.floor(i*math.sin(self.orientation) + self.pose.y)
                r = range(int(ty) - ROBOT_RADIUS, int(ty) + ROBOT_RADIUS + 1)
                if self.target.y in r:
                    return True

        return False

    def is_ball_y(self):
        return None
