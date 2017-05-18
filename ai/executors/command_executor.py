# Under MIT License, see LICENSE.txt
from typing import List

from RULEngine.Command.command import _Command
from RULEngine.Communication.util.serial_protocol import DribblerStatus
from RULEngine.Game.Player import Player
from ai.executors.executor import Executor
from RULEngine.Command import command
from RULEngine.Util.Pose import Pose
from ai.Util.ai_command import AICommand, AICommandType
from ai.states.world_state import WorldState


class CommandExecutor(Executor):
    def __init__(self, p_world_state: WorldState):
        """
        Initialise le CommandExecutor comme un simple executor

        :param p_world_state: (WorldState) instance du worldstate
        """
        super().__init__(p_world_state)

    def exec(self) -> List[_Command]:
        """
        Execute l'executor en transformant les ai_commandes produites au STA en command du RULEngine

        :return: List[_Command]
        """
        # Take last ai_commands
        ready_to_ship_robot_packet_list = []
        # Transform to other command type
        for player in self.ws.game_state.my_team.available_players.values():
            ready_to_ship_robot_packet_list.append(self._parse_ai_command(player.ai_command,
                                                                          player.id))
        return ready_to_ship_robot_packet_list

    def _parse_ai_command(self, ai_command: AICommand, player_id: int) -> _Command:
        """
        Transforme une ai_command en command d'envoi du RULEngine d'après certaines de ses caractéristiques

        :param ai_command: (AICommand) instance a transformée
        :param player_id: (int) id du joueur
        :return: (_Command) une command d'envoi du RULEngine correspondante
        """

        # TODO add a way to stop the dribbler! MGL 2017/03/14
        # TODO restraindre une seul commande de mouvement par robot
        if ai_command is not None:
            if ai_command.charge_kick:
                return self._generate_charge_kick_command(player_id)

            if ai_command.dribbler_on > 0:
                return self._generate_dribbler_command(player_id, ai_command.dribbler_on)

            if ai_command.kick:
                return self._generate_kick_command(player_id, ai_command.kick_strength)

            if ai_command.command == AICommandType.MOVE:
                assert (isinstance(ai_command.speed, Pose))
                return self._generate_move_command(player_id, ai_command.speed)

        return self._generate_empty_command(player_id)

    def _retrieve_player(self, player_id: int) -> Player:
        """
        retourne l'instance de notre joueur identifier par l'identifiant de joueur

        :param player_id: (int) l'identifiant du joueur
        :return: (Player) instance d'un de nos joueur
        """
        return self.ws.game_state.get_player(player_id)

    def _generate_kick_command(self, player_id: int, kick_strength: int) -> _Command:
        """
        Creer un commande de kick

        :param player_id: (int) l'identifiant du joueur
        :param kick_strength: (int) la force du kick
        :return: (Kick) une commande de kick
        """
        return command.Kick(self._retrieve_player(player_id), kick_strength)

    def _generate_move_command(self, player_id: int, speed: Pose) -> _Command:
        """
        Creer un commande de mouvement

        :param player_id: (int) l'identifiant du joueur
        :param speed: (Pose) instance du speed a appliquer au robot
        :return: (Move) une commande de deplacement du robot
        """
        return command.Move(self._retrieve_player(player_id), speed)

    def _generate_charge_kick_command(self, player_id: int) -> _Command:
        """
        Crée une commande de chargement du kick

        :param player_id: (int) l'identifiant du joueur
        :return: (ChargeKick) une commande de chargement du kick du robot
        """
        return command.ChargeKick(self._retrieve_player(player_id))

    def _generate_dribbler_command(self, player_id: int, status: int) -> _Command:
        """
        Crée une command de dribbleur

        :param player_id: (int) l'identifiant du joueur
        :param status: (int) la force du dribbleur?
        :return: (Dribbler) une commande d'activation du dribbleur
        """
        dribbler_status = False
        if status == 2:
            dribbler_status = True
        return command.Dribbler(self._retrieve_player(player_id), dribbler_status)

    def _generate_empty_command(self, player_id: int) -> _Command:
        """
        Crée un commande vide

        :param player_id: (int) l'identifiant du joueur
        :return: (Stop) une commande de stop
        """
        # Envoi d'une command vide qui fait l'arrêt du robot
        return command.Stop(self._retrieve_player(player_id))

    @staticmethod
    def _sanitize_kick_strength(p_kick_strength: int) -> int:
        """
        Retourn un kick strength adéquat

        :param p_kick_strength: (int) un strength de kick
        :return: (int) un kick sanitezer
        """
        if p_kick_strength > 1:
            print("Warning: kick strength devrait être contenu dans l'intervale [0, 1].")
            return 1
        else:
            return p_kick_strength
