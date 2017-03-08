# Under MIT License, see LICENSE.txt
from RULEngine.Util.geometry import Position, get_angle, get_distance
import timeit as t
import math as m
from StrategyIA.UltimateStrat.InfoManager import InfoManager

__author__ = 'RoboCupULaval'


class RVOPathfinder:
    """Pathfinder qui esquive les obstacles mobiles.

    Calcule un vecteur de base à suivre pour atteindre la cible.
    Ce vecteur sera modifié 10fois (2 projections par obstacle)
    pour prévoir leur déplacement et ainsi les esquiver.
    """

    def vector_generator(self, id_player, target):
        player = InfoManager.get_player_position(id_player)  # Position du joueur
        # target = InfoManager.get_ball_position()  # Position de la balle
        const_path = -10000  # Constante de réglage
        obstacles_list = []  # Liste des obstacles (de 1 à 6, le 0 étant celui qui va chercher la balle)
        for num in range(1, 6):  # On remplit la liste des obstacle avec la position de chacun (position, id)
            obstacles_list.append((InfoManager.get_player_position(num), num))
        theta = get_angle(player, target)  # angle entre le joueur et la balle
        begin = t.timeit()  # Pour calculer le temps

        if get_distance(player, target) > 150:  # Tant que la distance entre le robot est la balle > 100mm
            relative_vector = Position((player.x + m.cos(theta) * 100),
                                       (player.y + m.sin(theta) * 100))  # On donne un vecteur au robot à suivre
            print("Vecteur initial du robot à suivre: " + str(relative_vector))
            for obstacle in obstacles_list:  # Boucle pour chaque obstacle dans la liste
                alpha = get_angle(player, obstacle[0])  # Angle entre joueur et obstacle
                obstacle_velocity = InfoManager.get_speed(obstacle[1])  # Vitesse de l'obstacle obstacle[1]
                print("Vecteur vitesse de l'obstacle: " + str(obstacle[1]) + ": " + str(obstacle_velocity[
                                                                                            'vector']))
                projected_list = projection_calculation(obstacle, obstacle_velocity)  # Fonction de calcul
                dist = get_distance(player, obstacle[0])  # Distance joueur-obstacle
                dist_revised = const_path / dist  # Cte pour régler les vecteurs obstacles.
                obstacle_vector = Position(m.cos(alpha) * dist_revised,
                                           m.sin(alpha) * dist_revised)  # vecteur obstacle de base
                print("Vecteur de base est de: " + str(obstacle_vector))
                for projected_obstacle in projected_list:  # Pour chaque obstacle
                    # Distance entre joueur et la projection de l'obstacle
                    distance = get_distance(player, projected_obstacle)
                    distance_revised = const_path / distance  # Cte pour régler les vecteurs obstacles pondérés
                    # Vecteur de la projection de l'obstacle
                    projected_obstacle_vector = Position(m.cos(alpha) * distance_revised,
                                                         m.sin(alpha) * distance_revised)
                    # On ajoute le vecteur de la projection au vecteur obstacle de base
                    obstacle_vector += projected_obstacle_vector
                print("Vecteur après les projections est de: " + str(obstacle_vector))
                relative_vector += obstacle_vector  # On ajoute les vecteurs des projections au vecteur initial

            n = m.atan2(relative_vector.y - player.y, relative_vector.x - player.x)
            relative_vector = Position(player.x + m.cos(n) * 100,
                                       player.y + m.sin(n) * 100)  # Vecteur final du robot à suivre
            end = t.timeit()  # Le temps nécessaire pour calculer un nouveau vecteur
            print("\nTemps utilisé pour le calcul du vecteur final: " + str(abs(end - begin)) + " seconde")
            print("Vecteur final du robot à suivre: " + str(relative_vector) + "\n")
            return relative_vector
        else:
            return player
            # return {'skill': 'sFollowTarget', 'target': relative_vector, 'goal': target}
            # else:
            # return {'skill': 'sStop', 'target': player, 'goal': player}


def projection_calculation(obstacle, obstacle_velocity, projected_obstacle_list=None, delta_t=1, acceleration=1500):
    """Calcul de la projection d'un obstacle.

    argument:
    obstacle -- Numéro de l'obstacle
    obstacle_velocity -- Vitesse de l'obstacle
    projectedObstacleList -- Liste qui contient la projection de l'obstacle (vide par défaut)
    deltaT -- 1 Seconde
    acceleration -- Accélération du robot (par défaut 1500mm/s**2)

    """
    if projected_obstacle_list is None:
        projected_obstacle_list = []
    for i in range(2):
        # Calcul de la projection dans le axe des x
        projection_x = obstacle[0].x + float(obstacle_velocity['vector'][0]) * (delta_t * i / 50) \
                       + acceleration * ((delta_t * i / 50) ** 2) / 2
        # Calcul de la projection dans le axe des y
        projection_y = obstacle[0].y + float(obstacle_velocity['vector'][1]) * (delta_t * i / 50) \
                       + acceleration * ((delta_t * i / 50) ** 2) / 2
        # Projection des 2 prochaines positions de l’obstacle (à 0s et 0.02s)
        projection = Position(projection_x, projection_y)
        # On l'ajoute dans la liste (Projec1, Projec2)
        projected_obstacle_list.append(projection)
        print("Pour le robot numéro " + str(obstacle[1]) + " : Projection dans " + str(i / 50) + " seconde: " + str(
            projection))
    return projected_obstacle_list
