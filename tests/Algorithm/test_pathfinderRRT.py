# Under MIT license, see LICENSE.txt

import unittest

from ai.Algorithm.PathfinderRRT import get_expand_dis,get_goal_sample_rate,get_path_length, line_collision_check
from ai.states.InfoManager import InfoManager

__author__ = 'RoboCupULaval'


class TestPathinderRRT(unittest.TestCase):
    def setUp(self):
        self.info_manager = InfoManager()

    def test_get_expand_dis(self):
        # test la distance d'expansion quand la distance est supérieure à 600
        start = [-1000, 500]
        goal = [1000, 0]
        self.assertEqual(get_expand_dis(start, goal), 300)

        # test la distance d'expansion quand la distance est inférieure à 600
        start = [0, 0]
        goal = [0, 100]
        self.assertEqual(get_expand_dis(start, goal), 50)

        # test la distance d'expansion quand le début et l'arrivée sont None
        start = None
        goal = None
        self.assertEqual(get_expand_dis(start, goal),0)

    def test_get_goal_sample_rate(self):
        # test la fonction qui donne la probabilité d'obtenir directement le goal quand la distance est supérieure à 600
        start = [-1000,500]
        goal = [1000, 0]
        self.assertEqual(get_goal_sample_rate(start, goal), 30)

        # test la fonction qui donne la probabilité d'obtenir directement le goal quand la distance est inférieure à 600
        start = [0,0]
        goal = [0, 100]
        self.assertAlmostEqual(get_goal_sample_rate(start, goal), 86.22448979591839)

        # test la fonction qui donne la probabilité d'obtenir directement le goal quand les deux variables sont None.
        start = None
        goal = None
        self.assertEqual(get_goal_sample_rate(start, goal), 5)

    def test_get_path_length(self):
        # test la fonction qui donne la longueur du path
        path = [[100,0], [200,0], [300,0]]
        self.assertAlmostEqual(get_path_length(path), 200)
        # test la fonction qui donne la longueur du path quand le path est une liste vide
        path = []
        self.assertEqual(get_path_length(path), 0)
        # test la fonction qui donne la longueur du path quand le path est None
        path = None
        self.assertEqual(get_path_length(path), 0)

    def test_line_collision_check(self):
        obstacleList = [[100,100,300],[600,400,200]]
        first = [50,50]
        second = [0,0]
        self.assertFalse(line_collision_check(first,second,obstacleList))




if __name__ == "__main__":
    unittest.main()
