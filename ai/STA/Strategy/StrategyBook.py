# Under MIT license, see LICENSE.txt
""" Livre des stratégies. """

from abc import ABCMeta

from ..Tactic import tactic_constants
from ..Tactic.GoGetBall import GoGetBall
from ..Tactic.GoalKeeper import GoalKeeper
from ..Tactic.GoToPosition import GoToPosition
from ..Tactic.Stop import Stop
from ..Tactic.CoverZone import CoverZone

TACTIC_BOOK = {'goto_position' : GoToPosition,
               'goalkeeper' : GoalKeeper,
               'cover_zone' : CoverZone,
               'get_ball' : GoGetBall}

class StrategyBook(object):
    """
        Cette classe est capable de récupérer les stratégies enregistrés dans la
        configuration des stratégies et de les exposer au Behavior Tree en
        charge de sélectionner la stratégie courante.
    """
    def __init__(self):
        self.book = {'HumanControl': HumanControl}

    def get_strategy(self, strategy_name):
        return self.book[strategy_name]

    def get_strategies_name_list(self):
        return list(self.book.keys())

class Strategy(metaclass=ABCMeta):
    """ Définie l'interface commune aux stratégies. """
    def __init__(self, p_info_manager, p_starting_tactics_sequence):
        self.info_manager = p_info_manager
        self.tactics_sequence = []
        self._init_tactics_sequence(p_starting_tactics_sequence)

    def get_next_tactics_sequence(self):
        """
            Retourne 6 tactics, si la séquence de tactiques de la stratégie
            est épuiséee, les dernières tactiques sont *Stop*.
        """
        self._remove_finished_tactics()
        return self._generate_next_tactics_sequence()

    def _init_tactics_sequence(self, p_starting_tactics_sequence):
        for pid in range(6):
            self.tactics_sequence.append(p_starting_tactics_sequence[pid](self.info_manager, pid))

    def _remove_finished_tactics(self):
        for tactic in self.tactics_sequence:
            if  tactic_constants.is_complete(tactic.status_flag):
                self.tactics_sequence.remove(tactic)

    def _generate_next_tactics_sequence(self):
        next_tactics_sequence = []
        for pid in range(6):
            try:
                next_tactics_sequence.append(self.tactics_sequence[pid])
            except IndexError:
                next_tactics_sequence.append(Stop(self.info_manager, pid))
        return next_tactics_sequence

class HumanControl(Strategy):
    def __init__(self, p_info_manager):
        super().__init__(p_info_manager, [Stop, Stop, Stop, Stop, Stop, Stop])
