# Under MIT License, see LICENSE.txt
""" Module pour tester PlayExecutor """
from unittest import TestCase

from RULEngine.Game.Field import Field
from RULEngine.Game.Ball import Ball
from RULEngine.Game.Team import Team
from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose, Position

from AI.STP.Play.PlayBase import PlayBase
from AI.STP.Play.pHalt import pHalt
from AI.STP.Tactic.TacticBase import TacticBase
from AI.STP.Skill.SkillBase import SkillBase

from AI.InfoManager import InfoManager

__author__ = 'RoboCupULaval'

class TestPlayExecutor(TestCase):
    """ Unit test pour PlayExecutor """

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
            player.position = Position(-100 * player.id - 100, -100 * player.id - 100)
            #self.op_team.players[player.id].position = Position(-100 * player.id - 100, -100 * player.id - 100)

        self.field = Field(Ball())
        self.field.ball._position = Position(1000, 0)
        self.info = InfoManager(self.field, self.team, self.op_team)
        self.info.update()

        #simulate the CoachExecutor
        self.info.set_play('pHalt')
        self.info.init_play_sequence()

    def test_construction(self):
        self.assertNotEqual(self.playbook, None)
        self.assertNotEqual(self.tacticbook, None)
        self.assertNotEqual(self.skillbook, None)
        self.assertIsInstance(self.playbook, PlayBase)
        self.assertIsInstance(self.tacticbook, TacticBase)
        self.assertIsInstance(self.skillbook, SkillBase)


    def test_exec(self):
        # TODO: Trouver un moyen de simuler un Play dans un PlayBook
        current_play = 'pHalt'

        current_sequence = self.info.get_current_play_sequence()
        self.assertIsNotNone(current_sequence)
        self.assertTrue(current_sequence in range(self.info.get_count_player()))

        #If this line work then the play is in the playbook
        play = self.playbook.getBook()[current_play]
        self.assertTrue(play == pHalt)
        play = play()

        #tNull is the tactic for every robot in the play pHalt
        for i, tactic in enumerate(play.getTactics()):
            self.info.set_player_tactic(i, tactic)
            self.assertIs(self.info.get_player_tactic(i), 'tNull')

