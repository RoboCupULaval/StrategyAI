from ai.GameStateManager import GameStateManager
from ai.ModuleManager import ModuleManager
from ai.Algorithm.PathfinderRRT import PathfinderRRT
import unittest

class TestSingleton(unittest.TestCase):
    def setUp(self):
        self.GameStateManager1 = GameStateManager()
        self.GameStateManager2 = GameStateManager()
        self.ModuleManager1 = ModuleManager()
        self.ModuleManager2 = ModuleManager()

    def test_singleton(self):
        self.assertTrue(self.GameStateManager1 is self.GameStateManager2)
        self.assertTrue(self.ModuleManager1 is self.ModuleManager2)
