# Under MIT license, see LICENSE.txt

from abc import ABCMeta

from ..Tactic.Stop import Stop
from ..Tactic import tactic_constants


class Strategy(metaclass=ABCMeta):
    """ Définie l'interface commune aux stratégies. """
    def __init__(self, p_game_state, p_starting_tactics_sequence):
        self.game_state = p_game_state
        self.tactics_sequence = []
        self._init_tactics_sequence(p_starting_tactics_sequence)

    def get_next_tactics_sequence(self):
        """
            Retourne 6 tactics, si la séquence de tactiques de la stratégie
            est épuiséee, les dernières tactiques sont *Stop*.
        """
        # todo fix sequence in strategy NOT YET USED!
        # self._remove_finished_tactics()
        return self._generate_next_tactics_sequence()

    def get_name(self):
        return self.__class__.__name__

    def _init_tactics_sequence(self, p_starting_tactics_sequence):
        # TODO Find something better, maybe idk...
        for tactic in p_starting_tactics_sequence:
            self.tactics_sequence.append(tactic)

    def _remove_finished_tactics(self):
        status_flag = True

        for tactic in self.tactics_sequence:
            if not tactic_constants.is_complete(tactic.status_flag):
                status_flag = False

        if status_flag:
            try:
                self.tactics_sequence.pop(0)
            except IndexError:
                pass

    def _generate_next_tactics_sequence(self):
        current_tactic_lineup = []
        for i in range(0, 6):
            try:
                current_tactic_lineup.append(self.tactics_sequence[i])
            except IndexError:
                current_tactic_lineup.append(Stop)
        return current_tactic_lineup
