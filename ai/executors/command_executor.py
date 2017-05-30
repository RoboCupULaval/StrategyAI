# Under MIT License, see LICENSE.txt
from typing import List

from RULEngine.Command.command import *
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from ai.executors.executor import Executor
from ai.Util.ai_command import AICommandType
from ai.states.world_state import WorldState


class CommandExecutor(Executor):
    def __init__(self, world_state: WorldState):
        """
        Initialise le CommandExecutor comme un simple executor

        :param world_state: (WorldState) instance du worldstate
        """
        super().__init__(world_state)

    def exec(self) -> List[Command]:
        """
        Execute l'executor en transformant les ai_commandes produites au STA en command du RULEngine

        :return: List[_Command]
        """
        # Take last ai_commands
        ready_to_ship_robot_packet_list = []
        # Transform to other command type
        for player in self.ws.game_state.my_team.available_players.values():
            ready_to_ship_robot_packet_list.append(self._parse_ai_command(player))
        return ready_to_ship_robot_packet_list

    @staticmethod
    def _parse_ai_command(player: OurPlayer) -> Command:
        """
        Transforme une ai_command en command d'envoi du RULEngine d'après certaines de ses caractéristiques
        :param player: (OurPlayer) instance du joueur
        :return: (Command) une command d'envoi du RULEngine correspondante
        """

        # TODO add a way to stop the dribbler! MGL 2017/03/14
        # TODO restraindre une seul commande de mouvement par robot
        if player.ai_command is not None:
            if player.ai_command.charge_kick:
                return StartChargingKick(player)

            if player.ai_command.dribbler_on > 0:
                return Dribbler(player)

            if player.ai_command.kick:
                return Kick(player, player.ai_command.kick_strength)

            if player.ai_command.command == AICommandType.MOVE:
                assert (isinstance(player.ai_command.speed, Pose))
                return Move(player)

        return Stop(player)
