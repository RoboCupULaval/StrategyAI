#Under MIT License, see LICENSE.txt
from unittest import TestCase

from RULEngine.Game.Field import Field
from RULEngine.Game.Ball import Ball
from RULEngine.Game.Team import Team
from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose, Position

from UltimateStrat.STP.Play.PlayBase import PlayBase
from UltimateStrat.STP.Play.pHalt import pHalt
from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from UltimateStrat.STP.Skill.SkillBase import SkillBase

from UltimateStrat.InfoManager import InfoManager

__author__ = 'RoboCupULaval'

class TestPlayExecutor(TestCase):
    """
    This text unit is using static fonction that should be changed in the future,
    please change acordingly. It require at the moment a play inside the playbook named pHalt where
    every tactic is tNull for each robot.
    """

    def setUp(self):

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
        self.field.ball.position(Position(1000, 0))
        self.info = InfoManager(self.field, self.team, self.op_team)
        self.info.update()

        #simulate the CoachExecutor
        self.info.setPlay('pHalt')
        self.info.initPlaySequence()

    def test_construction(self):
        self.assertNotEqual(self.playbook, None)
        self.assertNotEqual(self.tacticbook, None)
        self.assertNotEqual(self.skillbook, None)
        self.assertIsInstance(self.playbook, PlayBase)
        self.assertIsInstance(self.tacticbook, TacticBase)
        self.assertIsInstance(self.skillbook, SkillBase)


    def test_exec(self):
        #Couldn't find a way to simulate a play inside the play book
        current_play = 'pHalt'

        current_sequence = self.info.getCurrentPlaySequence()
        self.assertIsNotNone(current_sequence)
        self.assertTrue(current_sequence in range(self.info.getCountPlayer()))

        #If this line work then the play is in the playbook
        play = self.playbook[current_play]
        self.assertTrue(play == pHalt)

        #tNull is the tactic for every robot in the play pHalt
        for i, tactic in enumerate(play.getTactics(current_sequence)):
            self.info.setPlayerTactic(i, tactic)
            self.assertIs(self.info.getPlayerTactic(i), 'tNull')

