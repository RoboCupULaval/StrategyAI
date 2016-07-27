#Under MIT License, see LICENSE.txt

from InfluenceMap import InfluenceMap
import time


__author__ = 'RoboCupULaval'

if __name__ == "__main__":

    current_time = time.time()

    IM = InfluenceMap(None, 100, strength_decay=0.85, effect_radius=25)

    print("Class creation        --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    # IM.add_point_and_propagate_influence(15, 45, IM._board, -100)
    # IM.add_point_and_propagate_influence(20, 45, IM._board, -100)
    # IM.add_point_and_propagate_influence(0, 0, IM._board, -100)
    # IM.add_point_and_propagate_influence(15, 0, IM._board, -100)
    # IM.add_point_and_propagate_influence(20, 20, IM._board, 100)
    # IM.add_point_and_propagate_influence(59, 0, IM._board, -100)
    # IM.add_point_and_propagate_influence(49, 0, IM._board, 100)
    # IM.add_point_and_propagate_influence(49, 89, IM._board, 100)
    # IM.add_point_and_propagate_influence(49, 89, IM._board, -100)

    print("Points Adding         --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    print("Finder Fonctions      --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    print("Diverse functions     --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    # IM.print_board_to_file()

    print("Clear & Print         --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()
