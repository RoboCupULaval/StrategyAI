# Under MIT License, see LICENSE.txt
"""
    Module intelligent contenant l'implementation d'un Rapidly exploring Random
    Tree. Le module contient une classe qui peut être instanciée et qui calcule
    les trajectoires des robots de l'équipe. Les détails de l'algorithme sont
    disponibles sur la page wikipedia. Code original http://myenigma.hatenablog.com
    /entry/2016/03/23/092002

"""
# FIXME IMPORT!
import copy
import math
import random
import time

from RULEngine.Debug.debug_interface import COLOR_ID_MAP, DEFAULT_PATH_TIMEOUT
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.IntelligentModule import Pathfinder

OBSTACLE_DEAD_ZONE = 700
TIME_TO_UPDATE = 1


class PathfinderRRT(Pathfinder):
    """
        La classe hérite de IntelligentModule pour définir sa propriété state.
        L'interface expose une méthode qui force le calcul de toutes les
        trajectoires. Celles-ci sont enregistrés par effet de bords dans le
        GameState.

        Une méthode permet de récupérer la trajectoire d'un robot spécifique.
    """

    def __init__(self, gamestate):
        """
            Constructeur, appel le constructeur de la classe mère pour assigner
            la référence sur l'InfoManager.

            :param info_manager: référence sur l'InfoManager
        """
        super().__init__(p_worldstate)
        self.paths = {}
        for i in range(6):
            self.paths[i] = []

        # self.last_timestamp = self.ws.game_state.get_timestamp()

    # Pour être conforme à la nouvelle interface à être changé
    # éventuellement mgl 2016/12/23
    # TODO(mgl): change this please!
    def get_next_point(self, robot_id=None):
        pass

    def update(self):
        pass

    def draw_path(self, path, pid=0):
        points = []
        for path_element in path:
            x = path_element.position.x
            y = path_element.position.y
            points.append((x,y))
        self.debug_interface.add_multiple_points(points, COLOR_ID_MAP[pid], width=5, link="path - " + str(pid),
                                                    timeout=DEFAULT_PATH_TIMEOUT)

    def get_path(self, pid=None, target=None):
        """
            Retourne la trajectoire du robot.

            :param pid: Identifiant du robot, 0 à 5.
            :return: Une liste de Pose, [Pose]
        """

        assert(isinstance(pid, int)), "Un pid doit être passé"
        assert(isinstance(target, Pose)), "La cible doit être une Pose"
        return self._compute_path(pid, target)


    def _compute_path(self, pid, target):
        """
            Cette méthode calcul la trajectoire pour un robot.

            :param pid: L'identifiant du robot, 0 à 5.
            :return: None
        """

        # TODO mettre les buts dans les obstacles
        list_of_pid = list(range(6))
        list_of_other_team_pid = list(range(6))
        list_of_pid.remove(pid)
        obstacleList = []
        for other_pid in list_of_pid:

            # TODO info manager changer get_player_position
            position = self.ws.game_state.get_player_pose(other_pid).position
            obstacleList.append([position.x, position.y, OBSTACLE_DEAD_ZONE])

        initial_position_of_main_player = self.ws.game_state.get_player_pose(pid).position

        for pid in list_of_other_team_pid:
            position = self.ws.game_state.get_player_pose(pid,False).position
            obstacleList.append([position.x, position.y, OBSTACLE_DEAD_ZONE])

        target_position_of_player = target.position
        target_orientation_of_player = target.orientation
        assert(isinstance(target_position_of_player, Position)), "La cible du joueur doit être une Position"
        try :
            target_position_of_player.x
            target_position_of_player.y
        except AttributeError:
            target_position_of_player = self.ws.game_state.get_player_pose(pid).position


        rrt = RRT(start=[initial_position_of_main_player.x,
                         initial_position_of_main_player.y],
                  goal=[target_position_of_player.x, target_position_of_player.y],
                  obstacleList=obstacleList,
                  # TODO Vérifier si le robot peut sortir du terrain
                  rand_area=[-4500, 4500],
                  expand_dis=get_expand_dis([initial_position_of_main_player.x,
                                             initial_position_of_main_player.y],
                                            [target_position_of_player.x, target_position_of_player.y]),
                  goal_sample_rate=get_goal_sample_rate([initial_position_of_main_player.x,
                                                         initial_position_of_main_player.y],
                                                        [target_position_of_player.x, target_position_of_player.y]))

        not_smoothed_path = rrt.planning(obstacleList)

        # Path smoothing
        maxIter = 100
        # Il faut inverser la liste du chemin lissé tout en retirant le point de départ
        smoothed_path = path_smoothing(not_smoothed_path, maxIter, obstacleList)
        smoothed_path = list(reversed(smoothed_path[:-1]))

        return self._smoothed_path_to_pose_list(smoothed_path, target_orientation_of_player)

    def _smoothed_path_to_pose_list(self, smoothed_path, target_orientation):
        smoothed_poses = []
        for point in smoothed_path:
            smoothed_poses.append(Pose(Position(point[0], point[1]), target_orientation))

        return smoothed_poses


class RRT():
    """
    Classe principale du pathfinder, contient les fonctions principales
    permettant de générer le path.
    """

    def __init__(self, start, goal, obstacleList, rand_area, expand_dis, goal_sample_rate, max_iteration=50):
        """
        Setting Parameter

        start: Position de départ [x,y]
        goal:  Destination [x,y]
        obstacleList: Position et taille des obstacles [[x,y,size],...]
        randArea: Ramdom Samping Area [min,max]
        expand_dis : Longueur des arêtes
        goal_sample_rate : Probabilité d'obtenir directement le goal comme position.
        Améliore la vitesse du RRT

        max_iteration : Nombre d'itération du path smoother

        """
        self.start = Node(start[0], start[1])
        self.end = Node(goal[0], goal[1])
        self.minrand = rand_area[0]
        self.maxrand = rand_area[1]
        self.expand_dis = expand_dis
        self.goal_sample_rate = goal_sample_rate
        self.max_iteration = max_iteration

    def planning(self, obstacleList):
        """Fonction qui s'occupe de faire le path"""
        initial_time = time.time()
        self.node_list = [self.start]
        #TODO changer le gros hack degueux pour la gestion de la loop infinie
        while True and time.time()-initial_time < TIME_TO_UPDATE:
            # Random Sampling

            if random.randint(0, 100) > self.goal_sample_rate:
                random_coordinates = [random.uniform(self.minrand, self.maxrand), random.uniform(self.minrand, self.maxrand)]
            else:
                random_coordinates = [self.end.x, self.end.y]

            # Find nearest node
            nind = self.get_nearest_list_index(self.node_list, random_coordinates)
            # print(nind)

            # expand tree
            nearest_node = self.node_list[nind]
            theta = math.atan2(random_coordinates[1] - nearest_node.y, random_coordinates[0] - nearest_node.x)

            new_node = copy.deepcopy(nearest_node)
            new_node.x += self.expand_dis * math.cos(theta)
            new_node.y += self.expand_dis * math.sin(theta)
            new_node.parent = nind

            if not self.__collision_check(new_node, obstacleList):
                continue

            self.node_list.append(new_node)

            # check goal
            dx = new_node.x - self.end.x
            dy = new_node.y - self.end.y
            d = math.sqrt(dx * dx + dy * dy)
            if d <= self.expand_dis:
                break

        path = [[self.end.x, self.end.y]]
        last_index = len(self.node_list) - 1
        while self.node_list[last_index].parent is not None:
            node = self.node_list[last_index]
            path.append([node.x, node.y])
            last_index = node.parent
        path.append([self.start.x, self.start.y])

        # TODO fix gros hack sale
        if time.time()-initial_time >=1 :
            path = [[self.start.x, self.start.y],[self.start.x, self.start.y]]
        return path

    def get_nearest_list_index(self, node_list, rnd):
        dlist = [(node.x - rnd[0]) ** 2 + (node.y - rnd[1]) ** 2 for node in node_list]
        minind = dlist.index(min(dlist))
        return minind

    def __collision_check(self, node, obstacleList):
        """ Permet de vérifier si le chemin passe à travers un obstacle"""

        for (ox, oy, size) in obstacleList:
            dx = ox - node.x
            dy = oy - node.y
            d = math.sqrt(dx * dx + dy * dy)
            if d <= size:
                return False  # collision

        return True  # safe


class Node():
    """
    RRT Node
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None


def get_expand_dis(start, goal):
    """Modifie la distance entre 2 noeuds selon la distance entre le départ et le but.
     Utile pour la précision et les performances."""
    try :
        dx = goal[0]-start[0]
        dy = goal[1]-start[1]
        d = math.sqrt(dx * dx + dy * dy)
        # TODO voir comment on regle ça
    except TypeError:
        d = 0
    if d < 600 :
        expand_dis = d/2

    else :
        expand_dis = 300

    return expand_dis


def get_goal_sample_rate(start, goal):
    """Modifie la probabilité d'obtenir directement le but comme point selon la distance entre le départ et le but.
     Utile pour la précision et les performances."""
    try :
        dx = goal[0]-start[0]
        dy = goal[1]-start[1]
        d = math.sqrt(dx * dx + dy * dy)
    except TypeError:
        goal_sample_rate = 5
        return goal_sample_rate

    if d < 600 :
        goal_sample_rate = (10-d/140)**2
    else :
        goal_sample_rate = 30

    return goal_sample_rate


def get_path_length(path):

    """Donne la longueur du trajet"""
    path_length = 0
    try :
        for i in range(len(path) - 1):
            dx = path[i + 1][0] - path[i][0]
            dy = path[i + 1][1] - path[i][1]
            d = math.sqrt(dx * dx + dy * dy)
            path_length += d
    except TypeError:
        pass

    return path_length


def get_target_point(path, targetL):
    l = 0
    ti = 0
    last_pair_len = 0
    for i in range(len(path) - 1):
        dx = path[i + 1][0] - path[i][0]
        dy = path[i + 1][1] - path[i][1]
        d = math.sqrt(dx * dx + dy * dy)
        l += d
        if l >= targetL:
            ti = i-1
            last_pair_len = d
            break
    try :
        partRatio = (l - targetL) / last_pair_len
    except ZeroDivisionError:
        partRatio = 0
    #  print(partRatio)
    #  print((ti,len(path),path[ti],path[ti+1]))

    x = path[ti][0] + (path[ti + 1][0] - path[ti][0]) * partRatio
    y = path[ti][1] + (path[ti + 1][1] - path[ti][1]) * partRatio
    #  print((x,y))

    return [x, y, ti]


def line_collision_check(first, second, obstacleList):
    """
    Vérifie si la ligne entre 2 noeuds entre en collision avec un obstacle.

    """
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

    for (ox, oy, size) in obstacleList:
        d = abs(a*ox+b*oy+c)/(math.sqrt(a*a+b*b))
        #  print((ox,oy,size,d))
        if d <= (size):
            #  print("NG")
            return False

    #  print("OK")

    return True  # OK


def path_smoothing(path, maxIter, obstacleList):
    # Elle ralentit légèrement  le tout, voir si améliorable
    """Permet de rendre le trajet obtenu avec le RRT plus lisse"""

    #  print("PathSmoothing")

    path_length = get_path_length(path)

    for i in range(maxIter):
        # Sample two points
        pick_points = [random.uniform(0, path_length), random.uniform(0, path_length)]
        pick_points.sort()
        #  print(pick_points)
        first = get_target_point(path, pick_points[0])
        #  print(first)
        second = get_target_point(path, pick_points[1])
        #  print(second)

        if first[2] <= 0 or second[2] <= 0:
            continue

        if (second[2]+1) > len(path):
            continue

        if second[2] == first[2]:
            continue

        # collision check
        if not line_collision_check(first, second, obstacleList):
            continue

        #Create New path
        new_path = []
        new_path.extend(path[:first[2]+1])
        new_path.append([first[0], first[1]])
        new_path.append([second[0], second[1]])
        new_path.extend(path[second[2]+1:])
        path = new_path
        path_length = get_path_length(path)

    return path

# taille terrain = 9000 x 6000


