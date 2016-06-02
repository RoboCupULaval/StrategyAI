#Under MIT License, see LICENSE.txt
from InfluenceMap import InfluenceMap
import time

__author__ = 'RoboCupULaval'

if __name__ == "__main__":

    current_time = time.time()

    IM = InfluenceMap(30.0, strengthdecay=0.9, effectradius=8)

    print("Class creation --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    IM.initialize_borders()

    print("Initial Setup  --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    IM.add_point_and_propagate_influence(15, 15, 100)
    # IM.add_point_and_propagate_influence(20, 15, 100)
    # IM.add_point_and_propagate_influence(10, 15, 100)
    # IM.add_point_and_propagate_influence(15, 30, 100)
    # IM.add_point_and_propagate_influence(15, 45, 100)
    # IM.add_point_and_propagate_influence(15, 100, 100)
    # IM.add_point_and_propagate_influence(30, 15, -100)
    # IM.add_point_and_propagate_influence(45, 15, -100)
    # IM.add_point_and_propagate_influence(60, 15, -100)
    # IM.add_point_and_propagate_influence(45, 45, 100)
    IM.add_point_and_propagate_influence(50, 50, -100)
    # IM.add_point_and_propagate_influence(130, 130, -100)
    # IM.add_point_and_propagate_influence(120, 130, 100)
    # IM.add_point_and_propagate_influence(130, 120, -100)
    # IM.add_point_and_propagate_influence(75, 75, 100)
    # IM.add_point_and_propagate_influence(75, 75, -100)


    print("Points Adding      --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    # print(IM.find_closest_point_of_strength_around(20, 20, 0))

    print(IM.find_points_of_strength_in_square(50, 50, 5, 0))
    print("Find closest       --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    print("Diverse functions  --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    IM.print_board_to_file()
    IM.clear_point_on_board()
    print("Clear & Print      --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()
