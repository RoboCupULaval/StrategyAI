# Under MIT licence, see LICENCE.txt
from typing import List

from Util import Pose
from Util.ai_command import AICommand
from ai.GameDomainObjects import Player
from ai.STA.Action import Action
from Util.ai_command import Idle
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

__author__ = 'RobocupULaval'


class Tactic(object):
    """
        Classe mère de toutes les tactiques
    """

    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args: List=None):
        """
        Initialise la tactic avec des valeurs

        :param game_state: L'état du monde pour le jeu en cours
        :param player: Le joueur executant la tactic
        :param target: Pose général pouvant être utilisé par les classes enfants comme elles veulent
        """
        assert isinstance(game_state, GameState), "Le game_state doit être un GameState"
        assert isinstance(player, Player), "Le player doit être un Player, non un '{}'".format(player)
        assert isinstance(target, Pose), "La target devrait être une Pose"

        self.game_state = game_state
        self.player = player
        self.player_id = player.id
        if args is None:
            self.args = []
        else:
            self.args = args

        self.current_state = self.halt
        self.next_state = self.halt
        self.status_flag = Flags.INIT
        self.target = target

    def halt(self) -> Idle:
        """
            S'exécute lorsque l'état courant est *Halt*. Générique pour arrêter n
            'importe quelles tactiques enfants

            :return: un nouvelle instance de l'action Idle pour le robot
        """
        self.next_state = self.halt
        return Idle

    def exec(self) -> AICommand:
        """
            Exécute une *Action* selon l'état courant

            :return: un AICommand
        """
        next_ai_command = self.current_state()
        if isinstance(next_ai_command, Action):
            raise RuntimeError("Action are deprecaded use CmdBuilder")
        if not isinstance(next_ai_command, AICommand):
            raise RuntimeError("A tactic MUST return an AICommand, not a {}. It's {} the cuprid.".format(type(next_ai_command), self.current_state))
        self.current_state = self.next_state
        return next_ai_command

    def get_name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__class__.__name__
