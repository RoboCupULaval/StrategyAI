from time import time

from RULEngine.Strategy.Strategy import Strategy
from RULEngine.Command import Command
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import *

from UltimateStrat.Executor.CoachExecutor import CoachExecutor
from UltimateStrat.Executor.PlayExecutor import PlayExecutor
from UltimateStrat.Executor.TacticExecutor import TacticExecutor
from UltimateStrat.Executor.SkillExecutor import SkillExecutor
from UltimateStrat.InfoManager import InfoManager


__author__ = 'jbecirovski'

class UltimateStrategy(Strategy):
    def __init__(self, field, referee, team, opponent_team, is_team_yellow=False):
        Strategy.__init__(self, field, referee, team, opponent_team)

        # Create InfoManager
        self.team.is_team_yellow = is_team_yellow
        self.info_manager = InfoManager(field, team, opponent_team)

        # Create Executors
        self.ex_coach = CoachExecutor(self.info_manager)
        self.ex_play = PlayExecutor(self.info_manager)
        self.ex_tactic = TacticExecutor(self.info_manager)
        self.ex_skill = SkillExecutor(self.info_manager)

    def on_start(self):
        self.info_manager.update()
        # Main Strategy sequence
        self.ex_coach.exec()
        self.ex_play.exec()
        self.ex_tactic.exec()
        self.ex_skill.exec()

        # ::COMMAND SENDER::
        for i in range(6):
            next_action = self.info_manager.getPlayerNextAction(i)
            if isinstance(next_action, Pose):

                # Move Manager :: if next action is Pose
                self._send_command(Command.MoveToAndRotate(self.team.players[i], self.team, next_action))
            elif isinstance(next_action, int):

                # Kick Manager :: if next action is int
                if not 0 < next_action <= 8:
                    next_action = 5
                self._send_command(Command.Kick(self.team.players[i], self.team, next_action))
                if get_distance(self.info_manager.getPlayerPosition(i), self.info_manager.getBallPosition()) > 150:
                    self.info_manager.setPlayerNextAction(i, self.info_manager.getPlayerPosition(i))
            else:

                # Path Manager :: if next action is list of Pose
                if get_distance(self.info_manager.getPlayerPosition(i), next_action[0].position) < 180:
                    next_pose = next_action.pop(0)
                    if len(next_action) == 0:
                        next_action = next_pose
                    self.info_manager.setPlayerNextAction(i, next_action)
                    self._send_command(Command.MoveToAndRotate(self.team.players[i], self.team, next_pose))
                else:
                    self._send_command(Command.MoveToAndRotate(self.team.players[i], self.team, next_action[0]))

    def on_halt(self):
        self.on_start()

    def on_stop(self):
        self.on_start()
