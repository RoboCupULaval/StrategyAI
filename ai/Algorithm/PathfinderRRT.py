# Under MIT License, see LICENSE.txt
"""
    Module intelligent contenant l'implementation d'un Rapidly exploring Random
    Tree. Le module contient une classe qui peut être instanciée et qui calcule
    les trajectoires des robots de l'équipe. Les détails de l'algorithme sont
    disponibles sur la page wikipedia.
"""
from .IntelligentModule import IntelligentModule
import random
import math
import copy

class RRT():
    u"""
    Class for RRT Planning
    """

    def __init__(self, start, goal, obstacleList, randArea, expandDis=300.0, goalSampleRate = 5, maxIter = 1000):
        u"""
        Setting Parameter

        start:Start Position [x,y]
        goal:Goal Position [x,y]
        obstacleList:obstacle Positions [[x,y,size],...]
        randArea: Ramdom Samping Area [min,max]

        """
        self.start = Node(start[0],start[1])
        self.end = Node(goal[0],goal[1])
        self.minrand = randArea[0]
        self.maxrand = randArea[1]
        self.expandDis = expandDis
        self.goalSampleRate = goalSampleRate
        self.maxIter = maxIter

    def Planning(self):
        u"""
        Path planning

        animation: flag for animation on or off
        """

        self.nodeList = [self.start]
        while True:
            # Random Sampling
            if random.randint(0, 100) > self.goalSampleRate:
                rnd = [random.uniform(self.minrand, self.maxrand), random.uniform(self.minrand, self.maxrand)]
            else:
                rnd = [self.end.x, self.end.y]

            # Find nearest node
            nind = self.GetNearestListIndex(self.nodeList, rnd)
            # print(nind)

            # expand tree
            nearestNode =self.nodeList[nind]
            theta = math.atan2(rnd[1] - nearestNode.y, rnd[0] - nearestNode.x)

            newNode = copy.deepcopy(nearestNode)
            newNode.x += self.expandDis * math.cos(theta)
            newNode.y += self.expandDis * math.sin(theta)
            newNode.parent = nind

            if not self.__CollisionCheck(newNode, obstacleList):
                continue

            self.nodeList.append(newNode)

            # check goal
            dx = newNode.x - self.end.x
            dy = newNode.y - self.end.y
            d = math.sqrt(dx * dx + dy * dy)
            if d <= self.expandDis:
                print("Goal!!")
                break

        path = [[self.end.x, self.end.y, 0]]
        lastIndex = len(self.nodeList) - 1
        while self.nodeList[lastIndex].parent is not None:
            node = self.nodeList[lastIndex]
            path.append([node.x, node.y, 0])
            lastIndex = node.parent
        path.append([self.start.x, self.start.y, 0])

        return path


    def GetNearestListIndex(self, nodeList, rnd):
        dlist = [(node.x - rnd[0]) ** 2 + (node.y - rnd[1]) ** 2 for node in nodeList]
        minind = dlist.index(min(dlist))
        return minind

    def __CollisionCheck(self, node, obstacleList):

        for (ox, oy, oz, size) in obstacleList:
            dx = ox - node.x
            dy = oy - node.y
            d = math.sqrt(dx * dx + dy * dy)
            if d <= size:
                return False  # collision

        return True  # safe

class Node():
    u"""
    RRT Node
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None


def GetPathLength(path):
    path_length = 0
    for i in range(len(path) - 1):
        dx = path[i + 1][0] - path[i][0]
        dy = path[i + 1][1] - path[i][1]
        d = math.sqrt(dx * dx + dy * dy)
        path_length += d

    return path_length


def GetTargetPoint(path, targetL):
    l = 0
    ti = 0
    lastPairLen = 0
    for i in range(len(path) - 1):
        dx = path[i + 1][0] - path[i][0]
        dy = path[i + 1][1] - path[i][1]
        d = math.sqrt(dx * dx + dy * dy)
        l += d
        if l >= targetL:
            ti = i-1
            lastPairLen = d
            break

    partRatio = (l - targetL) / lastPairLen
    #  print(partRatio)
    #  print((ti,len(path),path[ti],path[ti+1]))

    x = path[ti][0] + (path[ti + 1][0] - path[ti][0]) * partRatio
    y = path[ti][1] + (path[ti + 1][1] - path[ti][1]) * partRatio
    #  print((x,y))

    return [x, y, ti]


def LineCollisionCheck(first, second, obstacleList):
    # Line Equation

    x1 = first[0]
    y1 = first[1]
    x2 = second[0]
    y2 = second[1]

    try:
        a = y2-y1
        b = -(x2-x1)
        c = y2 * (x2-x1) - x2 * (y2-y1)
    except ZeroDivisionError:
        return False

    #  print(first)
    #  print(second)

    for (ox, oy, oz, size) in obstacleList:
        d = abs(a*ox+b*oy+c)/(math.sqrt(a*a+b*b))
        #  print((ox,oy,size,d))
        if d <= (size):
            #  print("NG")
            return False

    #  print("OK")

    return True  # OK


def path_smoothing(path, maxIter, obstacleList):
    #  print("PathSmoothing")

    path_length = GetPathLength(path)

    for i in range(maxIter):
        # Sample two points
        pickPoints = [random.uniform(0, path_length), random.uniform(0, path_length)]
        pickPoints.sort()
        #  print(pickPoints)
        first = GetTargetPoint(path, pickPoints[0])
        #  print(first)
        second = GetTargetPoint(path, pickPoints[1])
        #  print(second)

        if first[2] <= 0 or second[2] <= 0:
            continue

        if (second[2]+1) > len(path):
            continue

        if second[2] == first[2]:
            continue

        # collision check
        if not LineCollisionCheck(first, second, obstacleList):
            continue

        #Create New path
        new_path = []
        new_path.extend(path[:first[2]+1])
        new_path.append([first[0],first[1], 0])
        new_path.append([second[0],second[1], 0])
        new_path.extend(path[second[2]+1:])
        path = new_path
        path_length = GetPathLength(path)

    return path


if __name__ == '__main__':

    #====Search Path with RRT====
    # Parameter
    obstacleList = [
        (500, -500, 200),
        (-1500, 500, 200),
        (300, 80, 200),
        (-500, 1000, 200),
        (-1000, 500, 200),
        (0, -500, 200)
    ]  # [x,y,size]
    rrt = RRT(start=[4000,2500], goal=[-2000, 0], obstacleList=obstacleList, randArea=[-4500, 4500])
    path = rrt.Planning()

    # Draw final path




    #Path smoothing
    maxIter = 1000
    d_path = path_smoothing(path, maxIter, obstacleList)
    print(d_path)


#taille terrain = 9000 x 6000


class PathfinderRRT(IntelligentModule):
    """
        La classe hérite de IntelligentModule pour définir sa propriété state.
        L'interface expose une méthode qui force le calcul de toutes les
        trajectoires. Celles-ci sont enregistrés par effet de bords dans le
        GameState.

        Une méthode permet de récupérer la trajectoire d'un robot spécifique.
    """

    def __init__(self, pInfoManager):
        """
            Constructeur, appel le constructeur de la classe mère pour assigner
            la référence sur l'InfoManager.

            :param pInfoManager: référence sur l'InfoManager
        """
        super().__init__(pInfoManager)
        self.paths = {}
        for i in range(6):
            self.paths[i] = []


    def _compute_path(self, pid):

        """
            Cette méthode calcul la trajectoire pour un robot.

            :param pid: L'identifiant du robot, 0 à 5.
            :return: None
        """

        # TODO mettre les buts dans les obstacles
        obstacle_list = []







    def compute_paths(self):
        """
            Méthode qui lance le calcul de la trajectoire pour chaque robot de
            l'équipe.

            :return: None
        """
        pass

    def get_path(self, pid):
        """
            Retourne la trajectoire du robot.

            :param pid: Identifiant du robot, 0 à 5.
            :return: Une liste de Pose, [Pose]
        """
        pass

    def str(self):
        """ Affichage en String directe """
        return str(self.paths)
