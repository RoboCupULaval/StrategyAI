from abc import abstractmethod
from UltimateStrat.STP.Skill.SkillBase import SkillBase
from UltimateStrat.STP.Tactic.TacticBase import TacticBase
from UltimateStrat.STP.Play.PlayBase import PlayBase

__author__ = 'RoboCupULaval'


class Executor:
    def __init__(self, info_manager):
        self.info_manager = info_manager
        self.play_book = PlayBase()
        self.tactic_book = TacticBase()
        self.skill_book = SkillBase()

    @abstractmethod
    def exec(self):
        pass