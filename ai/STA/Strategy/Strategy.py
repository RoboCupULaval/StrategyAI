# Under MIT license, see LICENSE.txt

from abc import ABCMeta

from ..Tactic.Stop import Stop
from ..Tactic import tactic_constants


class Strategy(metaclass=ABCMeta):
    """ Définie l'interface commune aux stratégies. """
    def __init__(self, p_gamestatemanager, p_playmanager, p_starting_tactics_sequence):
        self.GameStateManager = p_gamestatemanager
        self.PlayManager = p_playmanager
        self.tactics_sequence = []
        self._init_tactics_sequence(p_starting_tactics_sequence)

    def set_next_tactics_sequence(self):
        """
            Retourne 6 tactics, si la séquence de tactiques de la stratégie
            est épuiséee, les dernières tactiques sont *Stop*.
        """
        # todo fix sequence in strategy NOT YET USED!
        # self._remove_finished_tactics()
        self._generate_next_tactics_sequence()

    def get_name(self):
        return self.__class__.__name__

    def _init_tactics_sequence(self, p_starting_tactics_sequence):
        for tactic in p_starting_tactics_sequence:
            self.tactics_sequence.append(tactic)

    def _remove_finished_tactics(self):
        for tactic in self.tactics_sequence:
            if tactic_constants.is_complete(tactic.status_flag):
                self.tactics_sequence.remove(tactic)

    def _generate_next_tactics_sequence(self):
        for i in range(0, 6):
            try:
                self.PlayManager.set_tactic(i, self.tactics_sequence[i])
            except IndexError:
                self.PlayManager.set_tactic(i, Stop(self.GameStateManager, self.PlayManager, i))
