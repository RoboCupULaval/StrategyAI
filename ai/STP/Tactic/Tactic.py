# Under MIT licence, see LICENCE.txt

__author__ = 'Robocup ULaval'

from abc import abstractmethod
from functools import wraps
from UltimateStrat import InfoManager
from Util import geometry
from UltimateStrat.STP.Skill import Action

class Tactique :
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
        self.current_state = "halt"
        self.next_state = "halt"

    def exec(self):
        self.dispatch()

    def halt(self):
        self.next_state = "halt"

    def dispatch(self):
        self.current_state = self.next_state

