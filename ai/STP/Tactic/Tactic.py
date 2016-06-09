# Under MIT licence, see LICENCE.txt

__author__ = 'Robocup ULaval'

from abc import abstractmethod
from functools import wraps
from ... import InfoManager
from ..Skill import Stop


class Tactic:
    """
    Classe mère de toutes les tactiques
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
        dispatch(self) : Trouve la fonction qui calcul le prochain état. est appelé après exec().
    attributs:
        info_manager: référence à la façade InfoManager
        team_id : Identifiant de l'équipe
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : chcîne de caratères définissant l'état courant
        next_state : chcîne de caratères définissant l'état suivant
    """

    def __init__(self, info_manager, team_id, player_id):
        self.info_manager = info_manager
        self.team_id = team_id
        self.player_id = player_id
        self.current_state = 'halt'
        self.next_state = 'halt'
        self.dispatch = {'halt': self.halt}

    def halt(self):
        arret = Stop(self.info_manager, self.player_id)
        self.next_state = 'halt'
        return arret

    def exec(self):
        # Trouver la prochaine action
        next_action = self.dispatch[self.current_state]()
        next_pose = next_action.exec()
        self.info_manager.set_player_next_action(self.player_id, next_pose)
        self.current_state = self.next_state
