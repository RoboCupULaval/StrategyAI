#Under MIT License, see LICENSE.txt
from InfluenceMap import InfluenceMap
import time

__author__ = 'RoboCupULaval'

if __name__ == "__main__":

    current_time = time.time()

    IM = InfluenceMap(50.0, strengthdecay=0.9, effectradius=40)

    print("Class creation --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    IM.initialize_borders()

    print("Initial Setup  --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()
    #
    # IM.point(15, 15, 100)
    # IM.point(20, 15, 100)
    # IM.point(10, 15, 100)
    # IM.point(15, 30, 100)
    # IM.point(15, 45, 100)
    # IM.point(15, 100, 100)
    # IM.point(30, 15, -100)
    # IM.point(45, 15, -100)
    # IM.point(60, 15, -100)
    # IM.point(45, 45, 100)
    # IM.point(50, 50, -100)
    # IM.point(75, 75, -100)
    # IM.point(43, 43, 100)
    # IM.point(5, 5, -100)
    # IM.point(75, 75, 100)
    # IM.point(120, 180, 100)
    # IM.point(90, 100, 100)
    # IM.point(100, 90, -100)
    # IM.point(100, 15, 100)
    # IM.point(100, 50, -100)
    #
    # IM.add_point_and_propagate_influence(15, 15, 100)
    # IM.add_point_and_propagate_influence(20, 15, 100)
    # IM.add_point_and_propagate_influence(10, 15, 100)
    # IM.add_point_and_propagate_influence(15, 30, 100)
    # IM.add_point_and_propagate_influence(15, 45, 100)
    # IM.add_point_and_propagate_influence(15, 100, 100)
    # IM.add_point_and_propagate_influence(30, 15, -100)
    # IM.add_point_and_propagate_influence(45, 15, -100)
    # IM.add_point_and_propagate_influence(60, 15, -100)
    # IM.add_point_and_propagate_influence(45, 45, 100)
    # IM.add_point_and_propagate_influence(50, 50, -100)
    # IM.add_point_and_propagate_influence(75, 75, -100)
    # IM.add_point_and_propagate_influence(43, 43, 100)
    # IM.add_point_and_propagate_influence(5, 5, -100)
    # IM.add_point_and_propagate_influence(75, 75, 100)
    # IM.add_point_and_propagate_influence(120, 180, 100)
    # IM.add_point_and_propagate_influence(90, 100, 100)
    # IM.add_point_and_propagate_influence(100, 90, -100)
    # IM.add_point_and_propagate_influence(100, 15, 100)
    # IM.add_point_and_propagate_influence(100, 50, -100)


    IM.add_point_and_propagate_stencil(15, 15, True)
    IM.add_point_and_propagate_stencil(20, 15, True)
    IM.add_point_and_propagate_stencil(10, 15, True)
    IM.add_point_and_propagate_stencil(15, 30, True)
    IM.add_point_and_propagate_stencil(15, 45, True)
    IM.add_point_and_propagate_stencil(15, 100, True)
    IM.add_point_and_propagate_stencil(30, 15, False)
    IM.add_point_and_propagate_stencil(45, 15, False)
    IM.add_point_and_propagate_stencil(60, 15, False)
    IM.add_point_and_propagate_stencil(45, 45, True)
    IM.add_point_and_propagate_stencil(50, 50, False)
    IM.add_point_and_propagate_stencil(75, 75, False)
    IM.add_point_and_propagate_stencil(43, 43, True)
    IM.add_point_and_propagate_stencil(5, 5, False)
    IM.add_point_and_propagate_stencil(75, 75, True)
    IM.add_point_and_propagate_stencil(120, 180, False)
    IM.add_point_and_propagate_stencil(90, 100, True)
    IM.add_point_and_propagate_stencil(100, 90, False)
    IM.add_point_and_propagate_stencil(100, 15, True)
    IM.add_point_and_propagate_stencil(100, 50, False)



    print("Points Adding      --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    #print(IM.find_closest_point_of_strength_around(20, 20, 0))
    #print(IM.find_closest_point_of_strength_around(100, 150, -1000, False))
    #print(IM.find_points_of_strength_in_square(50, 50, 5, 0))
    #print(IM.find_max_value_in_board())
    #print(IM.find_min_value_in_board())


    print("Find closest       --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    # print(IM.transform_board_to_field_position(0, 0))
    # print(IM.transform_board_to_field_position(60, 90))
    # print(IM.transform_board_to_field_position(120, 180))


    print("Diverse functions  --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()

    IM.print_board_to_file()
    IM.clear_point_on_board()

    print("Clear & Print      --- %s seconds ---" % (time.time() - current_time))
    current_time = time.time()
