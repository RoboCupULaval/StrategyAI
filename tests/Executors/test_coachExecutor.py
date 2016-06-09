# Under MIT License, see LICENSE.txt
""" Module de test pour CoachExecutor, nosetests style """
from nose.tools import assert_equal
from ai.InfoManager import InfoManager
from ai.Executor.CoachExecutor import CoachExecutor
from RULEngine.Game import Ball, Field, Player, Team

__author__ = 'RoboCupULaval'


class TestCoachExecutor:
    """ Class pour CoachExecutor """

    @classmethod
    def setup(cls):
        """ Setup """
        cls.info_manager = InfoManager()
        cls.coach = CoachExecutor(cls.info_manager)

    def test_exec(self):
        """ Test basic de exec, le prochain play et le play actuel ne concorde
            pas.
        """
        # FIXME: actuellement get_next_play retourne un play fix
        self.info_manager.set_play('pHalt')
        self.coach.exec()
        assert_equal(self.info_manager.get_current_play(), 'pTestBench')
