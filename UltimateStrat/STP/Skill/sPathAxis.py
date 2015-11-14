from UltimateStrat.STP.Skill.SkillBase import SkillBase
from RULEngine.Util.constant import *
from RULEngine.Util.Pose import Position, Pose
from math import *
import math

ROBOT_RADIUS = 90
BALL_RADIUS = 21
DEAD_ZONE = 100 

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
        self.orientation = pose_player.orientation
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
        print(ty)
        radius = int(ROBOT_RADIUS + BALL_RADIUS)

        angle = self.orientation
        angle_s = angle + math.pi/2

        # les +- 10 evitent un bogue (le robot va penser qu'il va collide la balle en se positionnant pour son drib)
        kx = self.kx(self.pose, self.target, angle)
        rx = range(int(kx*math.cos(angle)) + x - radius + 10, int(kx*math.cos(angle)) + x + radius + 1 - 10)
        ry = range(int(kx*math.sin(angle)) + y - radius + 10, int(kx*math.sin(angle)) + y + radius + 1 - 10)

        x_axis = tx in rx and ty in ry

        ky = self.ky(self.pose, self.target, angle_s)
        rx = range(int(ky*math.cos(angle_s)) + x - radius + 10, int(ky*math.cos(angle_s)) + x + radius + 1 - 10)
        ry = range(int(ky*math.sin(angle_s)) + y - radius + 10, int(ky*math.sin(angle_s)) + y + radius + 1 - 10)

        y_axis = tx in rx and ty in ry

        dribx = radius * math.cos(angle + math.pi) + tx
        driby = radius * math.sin(angle + math.pi) + ty
        drib = Position(int(dribx), int(driby))

        if angle >= math.pi/4 and angle < 3*math.pi/4:
            angle = self.orientation + math.pi/2
            t_axis = x_axis
            x_axis = y_axis
            y_axis = t_axis
        elif angle >= 5*math.pi/4 and angle < 7*math.pi/4:
            angle = self.orientation - math.pi/2
            t_axis = x_axis
            x_axis = y_axis
            y_axis = t_axis
        angle_s = angle + math.pi/2

        dead_delta = DEAD_ZONE
        deadx = int(drib.x) in range(x - dead_delta, x + dead_delta + 1)
        deady = int(drib.y) in range(y - dead_delta, y + dead_delta + 1)


        #debug
        print("X axis will collide: " + str(x_axis))
        print("Y axis will collide: " + str(y_axis))
        print("Drib position: " + str(drib))
        print("Dead in x: " + str(deadx))
        print("Dead in y: " + str(deady))
        print("Position du robot: " + str(self.pose) + ' <' + str(math.degrees(self.orientation)))

        if self.on_ball() or (x_axis and y_axis):
            self.paths = self.pose
        elif not x_axis and not deadx:
            # on bouge en "x axis" selon le robot
            k = self.kx(self.pose, drib, angle)
            deltax = int(k*cos(angle))
            deltay = int(k*sin(angle))
            self.paths = Position(x + deltax, y + deltay)
        elif not y_axis and not deady:
            # on bouge en 'y axis' selon le robot
            k = self.ky(self.pose, drib, angle_s)
            deltax = int(k*cos(angle_s))
            deltay = int(k*sin(angle_s))
            self.paths = Position(x + deltax, y + deltay)
        elif not deadx or not deady:
            # x_axis: True, y_axis: False
            kx = self.kx(self.pose, drib, angle)
            if kx > 0:
                # on va se positionner
                deltax = int(kx*math.cos(angle))
                deltay = int(kx*math.sin(angle))
                self.paths = Position(x + deltax, y + deltay)
            else:
                # on est du mauvaise cote de la balle, on va monter ou descendre
                k = 2*radius if y < 0 else -2*radius
                deltax = int(k*cos(angle_s))
                deltay = int(k*sin(angle_s))
                self.paths = Position(x + deltax, y + deltay)
        else:
            # on ne bouge pas
            self.paths = self.pose

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

        return int(ret)

    def on_ball(self):
        radius = int(ROBOT_RADIUS + BALL_RADIUS)
        x = int(self.pose.x)
        y = int(self.pose.y)
        tx = int(self.target.x)
        ty = int(self.target.y)

        rx = range(x - radius, x + radius + 1)
        ry = range(y - radius, y + radius + 1)
        return tx in rx and ty in ry
