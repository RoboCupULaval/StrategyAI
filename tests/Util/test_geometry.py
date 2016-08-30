# Under MIT License, see LICENSE.txt

import unittest
import math as m
import RULEngine.Util.geometry

__author__ = 'RoboCupULaval'

class TestGeometry(unittest.TestCase):

    def SetUp(self):
        self.position = RULEngine.Util.Position.Position()
        self.positionN = RULEngine.Util.Position.Position(0, 10000, 0)
        self.positionNE = RULEngine.Util.Position.Position(10000, 10000, 0)
        self.positionNO = RULEngine.Util.Position.Position(-10000, 10000, 0)
        self.positionS = RULEngine.Util.Position.Position(0, -10000, 0)
        self.positionSE = RULEngine.Util.Position.Position(10000, -10000, 0)
        self.positionSO = RULEngine.Util.Position.Position(-10000, -10000, 0)

    def test_get_distance(self):
        dist = RULEngine.Util.geometry.get_distance(self.position, self.positionN)
        self.assertEqual(dist, 1000)

        approx_dist = RULEngine.Util.geometry.get_distance(self.positionNE, self.positionSO)
        compValue = m.sqrt(2*(2000**2))
        self.assertAlmostEqual(approx_dist, compValue) # On veut quelle précision pour geo?

    def test_get_angle(self):
        self.assertEqual(RULEngine.Util.geometry.get_angle(self.positionN), (m.pi)/2)
        self.assertEqual(RULEngine.Util.geometry.get_angle(self.positionNE), (m.pi)/4)
        self.assertEqual(RULEngine.Util.geometry.get_angle(self.positionNO), 3*(m.pi)/4)
        self.assertEqual(RULEngine.Util.geometry.get_angle(self.positionSE), -1*(m.pi)/4)
        self.assertEqual(RULEngine.Util.geometry.get_angle(self.positionSO), -3*(m.pi)/4)

    def test_cvt_angle_360(self):
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360((m.pi)/4), 45)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360(3*(m.pi)/4), 135)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360(-3*(m.pi)/4), 225)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360(-1*(m.pi)/4), 345)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360(7*(m.pi)), 180)

    def test_cvt_angle_180(self):
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360((m.pi)/4), 45)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360(3*(m.pi)/4), 135)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360(-3*(m.pi)/4), -135)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360(-1*(m.pi)/4), -45)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360(7*(m.pi)), 180)

    def test_get_nearest(self):
        # Cas où on a des distances égales
        # Cas normal
        list_of_positions = [self.positionNE, self.positionSE, self.positionSO, self.positionN]
        self.assertEqual(RULEngine.Util.geometry.get_nearest(self.position, list_of_positions), self.positionN)

        list_of_positions.remove(self.positionN)
        list_of_positions.append(self.positionS)
        self.assertEqual(RULEngine.Util.geometry.get_nearest(self.position, list_of_positions), self.positionS)

    def test_get_milliseconds(self):
        self.assertEqual(RULEngine.Util.geometry.getmilliseconds(1.555555), 1555)

    def test_det(self):
        self.assertEqual(RULEngine.Util.geometry.det(self.positionNE, self.positionSO), 0)
        self.assertEqual(RULEngine.Util.geometry.det(self.positionNE, self.positionS), -1*(1000**2))

    def test_get_line_equation(self):
        self.assertEqual(RULEngine.Util.geometry.get_line_equation(self.positionNE, self.positionSO), {1, 0})

    def test_get_lines_intersection(self):


    def test_get_closest_point_on_line(self):

    def test_get_time_to_travel(self):

    def test_get_first_to_arrive(self):

    def test_angle_to_ball_is_tolerated(self):

    def test_get_required_kick_force(self): # simple calculation

