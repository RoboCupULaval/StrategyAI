from UltimateStrat.STP.Skill.SkillBase import SkillBase
from PythonFramework.Util.constant import *
from PythonFramework.Util.Pose import Position, Pose
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
        return self.paths

    def path(self):
        angle = self.orientation

        # Position relative aux abscisses
        x_axis = self.ball_on_axis()
        x_k = math.floor((self.target.x + BALL_RADIUS - (ROBOT_RADIUS + self.pose.x))/math.cos(self.orientation))

        # Position relative aux ordonnees
        y_axis = self.ball_on_axis(True)
        y_k = math.floor((self.target.y + BALL_RADIUS - ROBOT_RADIUS - self.pose.y)/math.sin(self.orientation + math.pi/2))

        # debug
        print(x_axis)
        print(y_axis)
        print('\n')

        # Calcul du prochain point
        if x_axis and not y_axis:
            if self.pose.y == self.target.y:
                if x_k > 0:
                    delta = min(self.target.x - self.pose.x - ROBOT_RADIUS - BALL_RADIUS, ROBOT_RADIUS)
                    deltax = delta*math.cos(angle)
                    deltay = delta*math.sin(angle)
                    self.paths = Position(self.pose.x + deltax, self.pose.y + deltay)
                else:
                    delta = -ROBOT_RADIUS if self.pose.y >= 0 else ROBOT_RADIUS
                    deltax = delta*math.sin(angle)
                    deltay = delta*math.cos(angle)
                    self.paths = Position(self.pose.x + deltax, self.pose.y + deltay)
            else:
                delta = self.target.y - self.pose.y
                deltax = delta*math.sin(angle)
                deltay = delta*math.cos(angle)
                self.paths = Position(self.pose.x, self.pose.y + delta)
        elif not x_axis and y_axis:
            delta = -ROBOT_RADIUS if self.pose.x >= 0 else ROBOT_RADIUS
            deltax = delta * math.cos(angle)
            deltay = delta * math.sin(angle)
            self.paths = Position(self.pose.x + deltax, self.pose.y + deltay)
        elif not x_axis and not y_axis:
            if x_k > 0:
                delta = ROBOT_RADIUS if self.target.y - self.pose.y >= 0 else -ROBOT_RADIUS
                deltax = delta*math.sin(angle)
                deltay = delta*math.cos(angle)
                self.paths = Position(self.pose.x + deltax, self.pose.y + deltay)
            else:
                delta = ROBOT_RADIUS
                deltax = delta*math.cos(angle)
                deltay = delta*math.sin(angle)
                self.paths = Position(self.pose.x - delta, self.pose.y)
        else:
            self.paths = self.pose

        return None

    def union(self, r1, r2):
        for i in r1:
            if i in r2:
                return True

        return False

    def ball_on_axis(self, y_axis=False):

        angle = self.orientation
        max = 0
        min = 0
        pos = 0
        target_pos = 0
        targets_pos = 0
        radius = int(ROBOT_RADIUS)
        f = math.cos
        if not y_axis:
            max = FIELD_X_RIGHT
            min = FIELD_X_LEFT
            pos = self.pose.x
            s_pos = self.pose.y
            target_pos = self.target.x
            targets_pos = self.target.y
            f = math.cos
            fs = math.sin
        else:
            angle += math.pi/2
            max = FIELD_Y_TOP
            min = FIELD_Y_BOTTOM
            pos = self.pose.y
            s_pos = self.pose.x
            target_pos = self.target.y
            targets_pos = self.target.x
            f = math.sin
            fs = math.cos

        k_max = math.ceil((max - pos)/f(angle)) + 1
        k_min = math.floor((min - pos)/f(angle))

        for i in range(k_min, k_max):
            # temporary position
            t_pos = math.floor(i*f(angle) + pos)
            if t_pos == target_pos:
                # temporary secondary position
                ts_pos = math.floor(i*fs(angle) + s_pos)
                r_pos = range(int(ts_pos) - radius, int(ts_pos) + radius + 1)
                r_target = range (int(targets_pos) - BALL_RADIUS, int(targets_pos) + BALL_RADIUS + 1)
                if self.union(r_pos, r_target):
                    return True

        return False
