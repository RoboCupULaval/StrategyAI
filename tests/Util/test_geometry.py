# Under MIT License, see LICENSE.txt

import unittest
import math as m
import RULEngine.Util.geometry

__author__ = 'RoboCupULaval'

class TestGeometry(unittest.TestCase):

    def SetUp(self):
        self.position = Position
        self.positionN = Position(0, 10000, 0)
        self.positionNE = Position(10000, 10000, 0)
        self.positionNO = Position(-10000, 10000, 0)
        self.positionSE = Position()
    def test_get_distance(self):



    def test_get_angle(self):


    def test_cvt_angle_360(self):

    def test_cvt_angle_180(self):

    def test_get_nearest(self):


    def test_get_milliseconds(self):


    def test_det(self):


    def test_get_line_equation(self):


    def test_get_lines_intersection(self):


    def test_get_closest_point_on_line(self):

    def test_get_time_to_travel(self):

    def test_get_first_to_arrive(self):

    def test_angle_to_ball_is_tolerated(self):

    def test_get_required_kick_force(self): # simple calculation

