
from RULEngine.Command import command
from RULEngine.Util.Pose import Pose


class RobotCommandManager(object):
    """
        Construit les commandes et les places dans un champ pour que Framework
        puissent les envoyer aux robots.
    """

    def __init__(self, p_gamestatemanager, p_debugmanager, p_playmanager):
        self.GameStateManager = p_gamestatemanager
        self.DebugManager = p_debugmanager
        self.PlayManager = p_playmanager
        self.robot_commands = []

    def update(self):
        self._generate_and_send_commands()

    def get_robots_commands(self):
        return self.robot_commands

    def _generate_and_send_commands(self):
        self._clear_commands()

        # FIXME this count annoys the shit out of me!
        for player_id in range(6):
            next_action = self.PlayManager.get_player_next_aicommand(player_id)
            robot_command = self._generate_command(next_action, player_id)
            self.robot_commands.append(robot_command)


    def _clear_commands(self):
        self.debug_commands.clear()
        self.robot_commands.clear()

    # todo see if we could make this better (ai command class? -> transform into -> robot command class here?)
    def _generate_command(self, p_next_action, player_id):
        if p_next_action is not None:

            if p_next_action.kick_strength > 0:
                return self._generate_kick_command(p_next_action.kick_strength, player_id)

            elif p_next_action.move_destination:
                assert(isinstance(p_next_action.move_destination, Pose))
                return self._generate_move_command(p_next_action.move_destination, player_id)

            else:
                return self._generate_empty_command(player_id)

        else:
            return self._generate_empty_command(player_id)

    def _generate_kick_command(self, p_kick_strength, player_id):
        kick_strength = self._sanitize_kick_strength(p_kick_strength)

        return command.Kick(player_id, kick_strength)

    def _generate_move_command(p_move_destination, player_id):
        return command.MoveToAndRotate(player_id, p_move_destination)

    def _generate_empty_command(self, player_id):
        # Envoie d'une command vide qui fait l'arrêt du robot
        player = self.GameStateManager.my_team.players[player_id]
        return command.Stop(player)

    def _send_robot_status(self):
        for player_id in range(6):
            try:

                robot_tactic = self.PlayManager.get_current_tactic(player_id).get_name()
                robot_action = self.PlayManager.get_current_action_name(player_id)
            except AttributeError as err:
                self.DebugManager.add_log(4,"Erreur lors de l'acquisition des données pour le robot: " + str(player_id)
                                          + " -- " + str(err))
                robot_tactic = 'None'
                robot_action = 'None'

            self.DebugManager.send_robot_status(player_id, robot_tactic, robot_action)

    @staticmethod
    def _sanitize_kick_strength(p_kick_strength):
        if p_kick_strength > 1:
            return 1
        else:
            return p_kick_strength
