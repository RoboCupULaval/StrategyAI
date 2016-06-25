# Under MIT licence, see LICENCE.txt

__author__ = 'Robocup ULaval'

from abc import abstractmethod
from functools import wraps
from ... import InfoManager
from ..Action import Stop


class Tactic:
    """
    Classe mère de toutes les tactiques
    """

    def __init__(self, pInfoManager, pTeamId, pPlayerId):
        """
            Initialise la tactique

            Lors de la création d'une nouvelle tactique, il faut ajouter
             les états de la tactique en utilisant self.dispatch.update().
             Sinon, on risque de perdre l'état halt

            :param pInfoManager: référence à la façade InfoManager
            :param  pTeamId : Identifiant de l'équipe
            :param pPlayerId : Identifiant du joueur auquel est assigné la tactique
        """
        self.info_manager = pInfoManager
        self.team_id = pTeamId
        self.player_id = pPlayerId
        self.current_state = 'halt'
        self.next_state = 'halt'
        self.dispatch = {'halt': self.halt}

    def halt(self):
        """
            S'exécute lorsque l'état Courant est en arrêt
            :return: l'action Stop crée
        """
        stop = Stop(self.info_manager, self.player_id)
        self.next_state = 'halt'
        return stop

    def exec(self):
        """
            Exécute une Action selon l'état courant
        """
        # Trouver la prochaine action
        next_action = self.dispatch[self.current_state]()
        next_pose = next_action.exec()
        self.info_manager.set_player_next_action(self.player_id, next_pose)
        self.current_state = self.next_state
