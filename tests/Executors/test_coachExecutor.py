# Under MIT License, see LICENSE.txt
""" Module de test pour CoachExecutor, nosetests style """
from nose.tools import assert_equal
from UltimateStrat.InfoManager import InfoManager
from UltimateStrat.Executor.CoachExecutor import CoachExecutor
from RULEngine.Game import Ball, Field, Player, Team

__author__ = 'RoboCupULaval'


class TestCoachExecutor:
    """ Class pour CoachExecutor """

    @classmethod
    def setup(cls):
        """ Setup """
        players = []
        for i in range(6):
            players.append(Player.Player(i))

        cls.info_manager = InfoManager(Field.Field(Ball.Ball()),
                                       Team.Team(players, True),
                                       Team.Team(players, False))
        cls.coach = CoachExecutor(cls.info_manager)

    def test_exec(self):
        """ Test basic de exec, le prochain play et le play actuel ne concorde
            pas.
        """
        # FIXME: actuellement get_next_play retourne un play fix
        self.info_manager.set_play('pHalt')
        self.coach.exec()
        assert_equal(self.info_manager.get_current_play(), 'pTestBench')
