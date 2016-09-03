# Under MIT License, see LICENSE.txt

import unittest
import math as m
import RULEngine.Util.geometry

__author__ = 'RoboCupULaval'

class TestGeometry(unittest.TestCase):

    def setUp(self):
        self.position = RULEngine.Util.Position.Position()
        self.positionN = RULEngine.Util.Position.Position(0, 10000, 0)
        self.positionNE = RULEngine.Util.Position.Position(10000, 10000, 0)
        self.positionNO = RULEngine.Util.Position.Position(-10000, 10000, 0)
        self.positionS = RULEngine.Util.Position.Position(0, -10000, 0)
        self.positionSE = RULEngine.Util.Position.Position(10000, -10000, 0)
        self.positionSO = RULEngine.Util.Position.Position(-10000, -10000, 0)

    def test_get_distance(self):
        dist = RULEngine.Util.geometry.get_distance(self.position, self.positionN)
        self.assertEqual(dist, 10000)

        approx_dist = RULEngine.Util.geometry.get_distance(self.positionNE, self.positionSO)
        compValue = m.sqrt(2*(20000**2))
        self.assertAlmostEqual(approx_dist, compValue) # On veut quelle précision pour geo?

    def test_get_angle(self):
        self.assertEqual(RULEngine.Util.geometry.get_angle(self.position, self.positionN), (m.pi)/2)
        self.assertEqual(RULEngine.Util.geometry.get_angle(self.position, self.positionNE), (m.pi)/4)
        self.assertEqual(RULEngine.Util.geometry.get_angle(self.position, self.positionNO), 3*(m.pi)/4)
        self.assertEqual(RULEngine.Util.geometry.get_angle(self.position, self.positionSE), -1*(m.pi)/4)
        self.assertEqual(RULEngine.Util.geometry.get_angle(self.position, self.positionSO), -3*(m.pi)/4)

    def test_cvt_angle_360(self):
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360((m.pi)/4), 45)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360(3*(m.pi)/4), 135)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360(-3*(m.pi)/4), 225)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360(-1*(m.pi)/4), 315)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_360(7*(m.pi)), 180)

    def test_cvt_angle_180(self):
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_180((m.pi)/4), 45)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_180(3*(m.pi)/4), 135)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_180(-3*(m.pi)/4), -135)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_180(-1*(m.pi)/4), -45)
        self.assertEqual(RULEngine.Util.geometry.cvt_angle_180(7*(m.pi)), 180)

    def test_get_nearest(self):
        # Cas où on a des distances égales
        # Cas normal
        list_of_positions = [self.positionNE, self.positionSE, self.positionSO, self.positionN]
        self.assertEqual(RULEngine.Util.geometry.get_nearest(self.position, list_of_positions), self.positionN)

        list_of_positions.remove(self.positionN)
        list_of_positions.append(self.positionS)
        self.assertEqual(RULEngine.Util.geometry.get_nearest(self.position, list_of_positions), self.positionS)

    def test_get_milliseconds(self):
        self.assertEqual(RULEngine.Util.geometry.get_milliseconds(1.555555), 1556)
        self.assertEqual(RULEngine.Util.geometry.get_milliseconds(1.444444), 1444)

    def test_det(self):
        self.assertEqual(RULEngine.Util.geometry.det(self.positionNE, self.positionSO), float(0))
        self.assertEqual(RULEngine.Util.geometry.det(self.positionNE, self.positionS), -1*(10000**2))

    def test_get_line_equation(self):
        self.assertEqual(RULEngine.Util.geometry.get_line_equation(self.positionNE, self.positionSO), (1, 0))

    def test_get_lines_intersection(self):
        no_intersection = RULEngine.Util.geometry.get_lines_intersection(self.positionS, self.positionN, self.positionNO, self.positionSO)
        infinite_position = RULEngine.Util.Position.Position(m.inf, m.inf)
        self.assertEqual(no_intersection, infinite_position)
        null_intersection = RULEngine.Util.geometry.get_lines_intersection(self.positionSE, self.positionNO, self.positionNE, self.positionSO)
        self.assertEqual(null_intersection, self.position)
        intersection = RULEngine.Util.geometry.get_lines_intersection(self.positionNE, self.positionNO, self.position, self.positionN)
        self.assertEqual(intersection, self.positionN)

    def test_get_closest_point_on_line(self):
        # Quand le point est nul (0, 0)
        close_null_point = RULEngine.Util.geometry.get_closest_point_on_line(self.positionNE, self.positionSE, self.positionNO)
        self.assertEqual(close_null_point, self.position)
        # Quand le point est sur une position à l'extérieure des deux points
        close_nonexistent_point = RULEngine.Util.geometry.get_closest_point_on_line(self.positionSE, self.position, self.positionN)
        self.assertEqual(close_nonexistent_point, self.positionS)
        # Point normal
        close_point = RULEngine.Util.geometry.get_closest_point_on_line(self.positionNE, self.position, self.positionN)
        self.assertEqual(close_point, self.positionN)

    def test_get_time_to_travel(self):
        null_time = RULEngine.Util.geometry.get_time_to_travel(0, 3, 2)
        self.assertEqual(null_time, 0)
        time_stop = RULEngine.Util.geometry.get_time_to_travel(10, 0, 0)
        self.assertEqual(time_stop, m.inf)
        time_constant = RULEngine.Util.geometry.get_time_to_travel(10, 3, 0)
        self.assertEqual(time_constant, 10/3)
        time_start = RULEngine.Util.geometry.get_time_to_travel(10, 0, 3)
        self.assertEqual(time_start, m.sqrt(120)/6)
        time = RULEngine.Util.geometry.get_time_to_travel(100, 5, 2)
        self.assertEqual(time, (m.sqrt(825)-5)/4)

    def test_get_first_to_arrive(self):
        neither = RULEngine.Util.geometry.get_first_to_arrive(120, 2, 3, 120, 2, 3)
        self.assertEqual(neither, 0)
        first = RULEngine.Util.geometry.get_first_to_arrive(100, 2, 3, 120, 2, 3)
        self.assertEqual(first, 1)
        second = RULEngine.Util.geometry.get_first_to_arrive(120, 2, 3, 100, 2, 3)
        self.assertEqual(second, 2)

    def test_angle_to_ball_is_tolerated(self):
        ball_position = self.positionN + RULEngine.Util.Position.Position(0, 5000, 0)
        not_tolerated = RULEngine.Util.geometry.angle_to_ball_is_tolerated(self.positionN, ball_position, self.positionS, m.pi/4)
        self.assertEqual(not_tolerated, False)
        ball_position = self.positionS + RULEngine.Util.Position.Position(0, 5000, 0)
        tolerated = RULEngine.Util.geometry.angle_to_ball_is_tolerated(self.positionS, ball_position, self.positionN, m.pi/4)
        self.assertEqual(tolerated, True)

    # def test_get_required_kick_force(self): # simple calculation

