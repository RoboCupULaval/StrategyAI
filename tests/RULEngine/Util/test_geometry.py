# Under MIT License, see LICENSE.txt

import math as m
import unittest

from Util import Position
from Util.geometry import get_line_equation, get_nearest, get_closest_point_on_line, get_distance

__author__ = 'RoboCupULaval'


class TestGeometry(unittest.TestCase):

    def setUp(self):
        self.position = Position()
        self.positionN = Position(0, 10000)
        self.positionNE = Position(10000, 10000)
        self.positionNO = Position(-10000, 10000)
        self.positionS = Position(0, -10000)
        self.positionSE = Position(10000, -10000)
        self.positionSO = Position(-10000, -10000)

    def test_get_distance(self):
        dist = get_distance(self.position, self.positionN)
        self.assertEqual(dist, 10000)

        approx_dist = (self.positionNE - self.positionSO).norm()
        compValue = m.sqrt(2*(20000**2))
        self.assertAlmostEqual(approx_dist, compValue) # On veut quelle précision pour geo?

    def test_get_angle(self):
        self.assertEqual((self.positionN - self.position).angle(), m.pi/2)
        self.assertEqual((self.positionNE - self.position).angle(), m.pi/4)
        self.assertEqual((self.positionNO - self.position).angle(), 3*m.pi/4)
        self.assertEqual((self.positionSE - self.position).angle(), -1*m.pi/4)
        self.assertEqual((self.positionSO - self.position).angle(), -3*m.pi/4)

    def test_get_nearest(self):
        list_of_positions = [self.positionNE, self.positionSE, self.positionSO, self.positionN]
        nearest = get_nearest(self.position, list_of_positions)
        self.assertEqual(nearest[0], self.positionN)

        list_of_positions.remove(self.positionN)
        list_of_positions.append(self.positionS)
        nearest = get_nearest(self.position, list_of_positions)
        self.assertEqual(nearest[0], self.positionS)


    def test_get_line_equation(self):
        self.assertEqual(get_line_equation(self.positionNE, self.positionSO), (1, 0))
        self.assertEqual(get_line_equation(self.positionNE, self.positionNO), (0, 10000))

    def test_get_closest_point_on_line(self):
        # Quand le point est nul (0, 0)
        close_null_point = get_closest_point_on_line(self.positionNE, self.positionSE, self.positionNO)
        self.assertEqual(close_null_point, self.position)
        # Quand le point est sur une position à l'extérieure des deux points
        close_nonexistent_point = get_closest_point_on_line(self.positionSE, self.position, self.positionN)
        self.assertEqual(close_nonexistent_point, self.positionS)
        # Point normal
        close_point = get_closest_point_on_line(self.positionNE, self.position, self.positionN)
        self.assertEqual(close_point, self.positionN)

    # def test_get_required_kick_force(self): # simple calculation

if __name__ == '__main__':
    unittest.main()