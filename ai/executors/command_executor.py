# Under MIT License, see LICENSE.txt
from RULEngine.Communication.util.serial_protocol import DribblerStatus
from ai.executors.executor import Executor
from RULEngine.Command import command
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.Util.ai_command import AICommand, AICommandType


class CommandExecutor(Executor):
    def __init__(self, p_world_state):
        super().__init__(p_world_state)

    def exec(self):
        ai_command_dict = self.ws.play_state.current_ai_commands
        ready_to_ship_robot_packet_list = []
        for player_id, ai_command in ai_command_dict.items():
            ready_to_ship_robot_packet_list.append(self._parse_ai_command(ai_command,
                                                                          player_id))

        return ready_to_ship_robot_packet_list

    def _parse_ai_command(self, ai_command: AICommand, player_id):
        # TODO restraindre une seul commande de mouvement par robot
        if ai_command.charge_kick:
            return self._generate_charge_kick_command(player_id)

        if ai_command.dribbler_on > 0:
            return self._generate_dribbler_command(player_id, ai_command.dribbler_on)

        if ai_command is not None:
            if ai_command.command == AICommandType.KICK:
                return self._generate_kick_command(player_id)

            elif ai_command.command == AICommandType.MOVE:
                assert (isinstance(ai_command.speed, Pose))
                return self._generate_move_command(ai_command.speed, player_id)

        return self._generate_empty_command(player_id)

    def _retrieve_player(self, player_id):
        return self.ws.game_state.my_team.players[player_id]

    def _generate_kick_command(self, player_id):
        return command.Kick(self._retrieve_player(player_id))

    def _generate_move_command(self, p_move_destination, player_id):
        return command.Move(self._retrieve_player(player_id), p_move_destination)

    def _generate_charge_kick_command(self, player_id):
        return command.ChargeKick(self._retrieve_player(player_id))

    def _generate_dribbler_command(self, player_id, status):
        dribbler_status = False
        if status == 2:
            dribbler_status = True
        return command.Dribbler(self._retrieve_player(player_id), dribbler_status)

    def _generate_empty_command(self, player_id):
        # Envoi d'une command vide qui fait l'arrêt du robot
        return command.Stop(self._retrieve_player(player_id))

    @staticmethod
    def _sanitize_kick_strength(p_kick_strength):
        if p_kick_strength > 1:
            print("Warning: kick strength devrait être contenu dans l'intervale [0, 1].")
            return 1
        else:
            return p_kick_strength
