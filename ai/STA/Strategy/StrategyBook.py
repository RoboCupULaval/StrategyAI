# Under MIT license, see LICENSE.txt

""" Livre des stratégies. """

from .HumanControl import HumanControl
from .SimpleDefense import SimpleDefense
from .TestAstarStrategy import TestAstarStrategy
from .SimpleOffense import SimpleOffense
from .DoNothing import DoNothing
from .WeirdmovementStrategy import WeirdmovementStrategy
from ai.STA.Strategy.TestTransitions import TestTransitions
from ai.STA.Strategy.TestPasses import TestPasses
from .TestRotateAround import TestRotateAround


class StrategyBook(object):
    """
        Cette classe est capable de récupérer les stratégies enregistrés dans
        la configuration des stratégies et de les exposer au Behavior Tree en
        charge de sélectionner la stratégie courante.
    """

    def __init__(self):
        self.strategy_book = {'SimpleDefense': SimpleDefense,
                              'SimpleOffense': SimpleOffense,
                              'HumanControl': HumanControl,
                              'DoNothing': DoNothing,
                              'TestTransitions': TestTransitions,
                              "TestRotateAround": TestRotateAround,
                              'WeirdmovementStrategy': WeirdmovementStrategy,
                              'TestPasses': TestPasses,
                              }

    def get_strategies_name_list(self):
        return list(self.strategy_book.keys())

    def get_strategy(self, strategy_name):
        if self.check_existance_strategy(strategy_name):
            return self.strategy_book[strategy_name]
        return self.strategy_book['DoNothing']

    def check_existance_strategy(self, strategy_name):
        assert isinstance(strategy_name, str)

        return strategy_name in self.strategy_book
