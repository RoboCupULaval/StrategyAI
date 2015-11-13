from UltimateStrat.STP.Skill.SkillBase import SkillBase
from RULEngine.Util.constant import *
from RULEngine.Util.Pose import Position, Pose
from math import *
import math

ROBOT_RADIUS = 90
BALL_RADIUS = 21

class sPathAxis(SkillBase):
    """
    PFAxisExecutor (PathFinder Axis) est une sequence de requetes permettant
    de fournir le pathfinder pour un seul robot qui cherche a se positionner
    pour kick la balle.
    1 - Ou est le robot?
    2 - Quelle est l'orientation du robot?
    3 - Ou est la balle?
    4 - Quel chemin doit-il emprunter pour avoir le dribbler sur la balle?
    """
    def __init__(self):
        SkillBase.__init__(self, self.__class__.__name__)
        self.pose = Position(0, 0)
        self.orientation = 0
        self.target = Position(-99999, -99999)
        self.paths = None

    def act(self, pose_player, pst_target, pst_goal):
        # 1 Ou est le robot
        self.pose = pose_player.position

        # 2 Quelle est l'orientation
        self.orientation = self.orientation
        self.orientation = math.radians(self.orientation)

        # 3 Position de la target
        self.target = pst_target

        # 4 Chemin a emprunter
        self.path()
        ret = self.paths
        return Pose(ret, 0)

    def path(self):
        x = int(self.pose.x)
        tx = int(self.target.x)
        y = int(self.pose.y)
        ty = int(self.target.y)
        radius = int(ROBOT_RADIUS + BALL_RADIUS)
        angle = self.orientation
        angle_s = self.orientation + math.pi/2

        c = cos(angle)
        s = sin(angle)

        kx = self.kx(self.pose, self.target, angle)
        ky = self.ky(self.pose, self.target, angle)

        #x_axis = self.union(rx, ry)

        c = cos(angle_s)
        s = sin(angle_s)
        rx = range(int((tx - x)/c - radius/c), int((tx - x)/c + radius/c + 1))
        ry = range(int((ty - y)/s - radius/s), int((ty - y)/s + radius/s + 1))

        y_axis = self.union(rx, ry)

        drib_posx = int(radius * math.cos(angle + math.pi) + tx)
        drib_posy = int(radius * math.sin(angle + math.pi) + ty)

        if x_axis and y_axis:
            self.paths(self.pose)
        elif not x_axis:
            # on bouge en "x axis" selon le robot
            k = self.kx(self.pose, self.target, angle)
            deltax = k*cos(angle)
            deltay = k*sin(angle)
            self.paths(x + deltax, y + deltay)

        self.paths = Position(drib_posx, drib_posy)
        return None

    def union(self, r1, r2):
        ret = False
        for i in r1:
            if i in r2:
                ret = True
        return ret

    def kx(self, pos1, pos2, angle):
        """ Retourne k pour le mouvement pour """
        x = pos1.x
        tx = pos2.x

        if angle < 0:
            angle = angle + math.pi
        angle = angle % (math.pi*2)
        ret = 0
        if not (angle == math.pi/2 or angle == (2*math.pi/3)):
            ret = int((tx - x)/cos(angle))

        return ret

    def ky(self, pos1, pos2, angle):
        y = pos1.y
        ty = pos2.y

        if angle < 0:
            angle = abs(angle) + math.pi
        angle = angle % (math.pi*2)
        ret = 0

        if not (angle == 0 or angle == math.pi):
            ret = int((ty - y)/sin(angle))

        return ret

    def radf(self, f, r, angle):
        if angle < 0:
            angle += math.pi
        angle = angle % (math.pi*2)

        ret = 0
        if f == math.sin and not (angle == 0 or angle == math.pi):
            ret = r / f(angle)
        elif f == math.cos and not (angle == math.pi/2 or angle == 2*math.pi/3):
            ret = r / f(angle)

        return ret
