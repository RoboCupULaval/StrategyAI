# Under MIT License, see LICENSE.txt
""" Module de test pour TacticExecutor """
from unittest import TestCase


from RULEngine.Game.Field import Field
from RULEngine.Game.Ball import Ball
from RULEngine.Game.Team import Team
from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Position

from UltimateStrat.STP.Play.PlayBase import PlayBase
from UltimateStrat.STP.Tactic.tNull import tNull
from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from UltimateStrat.STP.Skill.SkillBase import SkillBase

from UltimateStrat.InfoManager import InfoManager


__author__ = 'RoboCupULaval'


class TestTacticExecutor(TestCase):
    """ Class de test pour TacticExecutor """

    def setUp(self):
        """ Set up """

        self.playbook = PlayBase()
        self.tacticbook = TacticBase()
        self.skillbook = SkillBase()

        # Initialise InfoManager with teams, field, play, tactic and skill.
        self.team = Team([Player(bot_id) for bot_id in range(6)], True)
        for player in self.team.players:
            self.team.players[player.id].position = Position(100 * player.id, 100 * player.id)

        self.op_team = Team([Player(bot_id) for bot_id in range(6)], False)
        for player in self.op_team.players:
            pos_x = -100 * player.id - 100
            pos_y = -100 * player.id - 100
            self.op_team.players[player.id].position = Position(pos_x, pos_y)

        self.field = Field(Ball())
        self.field.ball.set_position(Position(1000, 0), 1)
        self.info = InfoManager(self.field, self.team, self.op_team)
        self.info.update()

        # simulate the CoachExecutor without the static function getcurrentplay from the infomanager
        self.info.set_play('pHalt')
        self.info.init_play_sequence()

        # simulate the PlayExecutor with a known play
        current_play = 'pHalt'
        play = self.playbook[current_play]
        play = play()

        tactics = play.getTactics()
        for i, t in enumerate(tactics):
            print("id: " + str(i) + " -- tactic: " + str(t))
            self.info.set_player_tactic(i, t)



    def test_construction(self):
        self.assertNotEqual(self.playbook, None)
        self.assertNotEqual(self.tacticbook, None)
        self.assertNotEqual(self.skillbook, None)
        self.assertIsInstance(self.playbook, PlayBase)
        self.assertIsInstance(self.tacticbook, TacticBase)
        self.assertIsInstance(self.skillbook, SkillBase)

    def test_exec(self):
        for id_player in range(self.info.get_count_player()):
            self.assertTrue(id_player in range(self.info.get_count_player()))

            current_tactic = self.info.get_player_tactic(id_player)
            self.assertIs(current_tactic, 'tNull')
            self.assertTrue(current_tactic == 'tNull')

            tactic = self.tacticbook[current_tactic]
            self.assertTrue(tactic == tNull)
            self.assertIs(tactic, tNull)

            action = tactic().apply(self.info, id_player)
            self.info.set_player_skill_target_goal(id_player, action)
            self.assertIs(self.info.get_player_skill(id_player), 'sNull')
            self.assertIs(self.info.get_player_goal(id_player),
                          self.info.get_player_position(id_player))
            self.assertIs(self.info.get_player_target(id_player),
                          self.info.get_player_position(id_player))
