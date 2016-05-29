#Under MIT License, see LICENSE.txt
from unittest import TestCase


from RULEngine.Game.Field import Field
from RULEngine.Game.Ball import Ball
from RULEngine.Game.Team import Team
from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose, Position

from UltimateStrat.STP.Play.PlayBase import PlayBase
from UltimateStrat.STP.Tactic.tNull import tNull
from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from UltimateStrat.STP.Skill.SkillBase import SkillBase

from UltimateStrat.InfoManager import InfoManager


__author__ = 'RoboCupULaval'


class TestTacticExecutor(TestCase):

    def setUp(self):
        """
        This text unit is using static fonction that should be changed in the future,
        please change acordingly. It require at the moment a play inside the playbook named pHalt where
        every tactic is tNull for each robot. It requires tNull to return sNull for each robot.
        """

        self.playbook = PlayBase()
        self.tacticbook = TacticBase()
        self.skillbook = SkillBase()

        #Initialise InfoManager with teams, field, play, tactic and skill.
        self.team = Team([Player(bot_id) for bot_id in range(6)], True)
        for player in self.team.players:
          self.team.players[player.id].position = Position(100 * player.id, 100 * player.id)

        self.op_team = Team([Player(bot_id) for bot_id in range(6)], False)
        for player in self.op_team.players:
          self.op_team.players[player.id].position = Position(-100 * player.id - 100, -100 * player.id - 100)

        self.field = Field(Ball())
        self.field.ball.set_position(Position(1000, 0), 1)
        self.info = InfoManager(self.field, self.team, self.op_team)
        self.info.update()

        #simulate the CoachExecutor without the static function getcurrentplay from the infomanager
        self.info.setPlay('pHalt')
        self.info.initPlaySequence()

        #simulate the PlayExecutor with a known play
        current_play = 'pHalt'
        current_sequence = self.info.getCurrentPlaySequence()
        play = self.playbook[current_play]
        for i, tactic in enumerate(play.getTactics(current_sequence)):
          self.info.setPlayerTactic(i, tactic)



    def test_construction(self):
        self.assertNotEqual(self.playbook, None)
        self.assertNotEqual(self.tacticbook, None)
        self.assertNotEqual(self.skillbook, None)
        self.assertIsInstance(self.playbook, PlayBase)
        self.assertIsInstance(self.tacticbook, TacticBase)
        self.assertIsInstance(self.skillbook, SkillBase)

    def test_exec(self):
        for id_player in range(self.info.getCountPlayer()):
            self.assertTrue(id_player in range(self.info.getCountPlayer()))

            current_tactic = self.info.getPlayerTactic(id_player)
            self.assertIs(current_tactic, 'tNull')
            self.assertTrue(current_tactic == 'tNull')

            tactic = self.tacticbook[current_tactic]
            self.assertTrue(tactic == tNull)
            self.assertIs(tactic, tNull)

            action = tactic().apply(self.info, id_player)
            self.info.setPlayerSkillTargetGoal(id_player, action)
            self.assertIs(self.info.getPlayerSkill(id_player), 'sNull')
            self.assertIs(self.info.getPlayerGoal(id_player), self.info.getPlayerPosition(id_player))
            self.assertIs(self.info.getPlayerTarget(id_player), self.info.getPlayerPosition(id_player))


