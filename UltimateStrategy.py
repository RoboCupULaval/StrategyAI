from PythonFramework.Strategy.Strategy import Strategy

from UltimateStrat.Executor.CoachExecutor import CoachExecutor
from UltimateStrat.Executor.PlayExecutor import PlayExecutor
from UltimateStrat.Executor.TacticExecutor import TacticExecutor
from UltimateStrat.Executor.SkillExecutor import SkillExecutor
from UltimateStrat.InfoManager import InfoManager

__author__ = 'jbecirovski'

class UltimateStrategy(Strategy):
    def __init__(self, field, referee, team, opponent_team):
        Strategy.__init__(self, field, referee, team, opponent_team)

        # Create Executors
        self.ex_coach = CoachExecutor(self.info_manager)
        self.ex_play = PlayExecutor(self.info_manager)
        self.ex_tactic = TacticExecutor(self.info_manager)
        self.ex_skill = SkillExecutor(self.info_manager)

        # Create InfoManager
        self.info_manager = InfoManager(field, team, opponent_team)

    def on_start(self):
        # Main Strategy sequence
        self.ex_coach.exec()
        self.ex_play.exec()
        self.ex_tactic.exec()
        self.ex_skill.exec()

    def on_halt(self):
        self.on_start()

    def on_stop(self):
        self.on_start()
