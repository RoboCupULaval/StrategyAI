# Under MIT License, see LICENSE.txt
from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Game.Referee import RefereeCommand
from ai.executors.executor import Executor
from ai.states.world_state import WorldState
from config.config_service import ConfigService

autonomousStrategies = {
    # Robots must be stopped
    'HALT' : 'DoNothing',

    # Robots must stay 50 cm from the ball
    'STOP' : 'DoNothing',
    'GOAL_US' : 'DoNothing',
    'GOAL_THEM' : 'DoNothing',
    'BALL_PLACEMENT_THEM' : 'DoNothing',

    # Place the ball to the designated position
    'BALL_PLACEMENT_US' : 'DoNothing',

    # The ball is free to take
    'FORCE_START' : 'DoNothing',

    'TIMEOUT' : 'DoNothing',

    'PREPARE_OFFENSIVE_KICKOFF' : 'DoNothing',
    'PREPARE_DEFENSIVE_KICKOFF' : 'DoNothing',
    'OFFENSIVE_KICKOFF' : 'DoNothing',
    'DEFENSIVE_KICKOFF' : 'DoNothing',

    'PREPARE_OFFENSIVE_PENALTY' : 'DoNothing',
    'PREPARE_DEFENSIVE_PENALTY' : 'DoNothing',
    'OFFENSIVE_PENALTY' : 'DoNothing',
    'DEFENSIVE_PENALTY' : 'DoNothing'
}


class PlayExecutor(Executor):

    def __init__(self, p_world_state: WorldState):
        """
        initialise le PlayExecutor

        :param p_world_state: (WorldState) instance du worldstate
        """
        super().__init__(p_world_state)

        self.ws.play_state.set_strategy(self._get_new_strategy('HALT'))
        self.last_ref_command = RefereeCommand.HALT

    def exec(self) -> None:
        """
        Execute la stratégie courante et envoie le status des robots et les livres de tactiques et stratégies

        :return: None
        """
        # TODO use handshake with the UI-DEBUG to stop sending it every frame! MGL 2017/03/16
        self._send_books()
        self.ws.debug_interface.send_team_color()
        #
        # DebugInterface().send_team_color(str(ConfigService().config_dict["GAME"]["our_color"]))

        if self.ws.play_state.autonomous_flag:
            self._select_strategy()
        self._send_auto_state()

        self._execute_strategy()
        # TODO reduce the frequency at which we send it maybe? MGL 2017/03/16
        self._send_robots_status()

    def _select_strategy(self) -> None:

        play_state = self.ws.play_state
        referee = self.ws.game_state.game.referee

        if self.last_ref_command != referee.command:
            if referee.command == RefereeCommand.HALT:
                DebugInterface().add_log(1, "Halt robots!")
                play_state.autonomous_state = 'HALT'

            elif referee.command == RefereeCommand.STOP or\
                    referee.command == RefereeCommand.GOAL_US or\
                    referee.command == RefereeCommand.GOAL_THEM or\
                    referee.command == RefereeCommand.BALL_PLACEMENT_THEM:
                DebugInterface().add_log(1, "Game stopped : Robots must keep 50 cm from the ball")
                play_state.autonomous_state = 'STOP'

            elif referee.command == RefereeCommand.BALL_PLACEMENT_US:
                DebugInterface().add_log(1, "Ball placement : we need to place the ball at : " + str(referee.ball_placement_point))
                play_state.autonomous_state = 'HALT' #TODO send ball new position to strategy...

            elif referee.command == RefereeCommand.FORCE_START:
                DebugInterface().add_log(1, "Force start : ball is free!")
                play_state.autonomous_state = 'FORCE_START'

            elif referee.command == RefereeCommand.NORMAL_START:
                DebugInterface().add_log(1, "Normal start")
                if self.last_ref_command == RefereeCommand.PREPARE_KICKOFF_US:
                    play_state.autonomous_state = 'OFFENSE_KICKOFF'
                elif self.last_ref_command == RefereeCommand.PREPARE_KICKOFF_THEM:
                    play_state.autonomous_state = 'DEFENSE_KICKOFF'
                elif self.last_ref_command == RefereeCommand.PREPARE_PENALTY_US:
                    play_state.autonomous_state = 'OFFENSE_PENALTY'
                elif self.last_ref_command == RefereeCommand.PREPARE_PENALTY_THEM:
                    play_state.autonomous_state = 'DEFENSE_PENALTY'

            elif referee.command == RefereeCommand.TIMEOUT_BLUE or\
                referee.command == RefereeCommand.TIMEOUT_YELLOW:
                DebugInterface().add_log(1, "Timeout!")
                play_state.autonomous_state = 'TIMEOUT'

            elif referee.command == RefereeCommand.PREPARE_KICKOFF_US:
                DebugInterface().add_log(1, "Prepare kickoff offense!")
                play_state.autonomous_state = 'PREPARE_KICKOFF_OFFENSE'

            elif referee.command == RefereeCommand.PREPARE_KICKOFF_THEM:
                DebugInterface().add_log(1, "Prepare kickoff defense!")
                play_state.autonomous_state = 'PREPARE_KICKOFF_DEFENSE'

            elif referee.command == RefereeCommand.PREPARE_PENALTY_US:
                DebugInterface().add_log(1, "Prepare penalty offense!")
                play_state.autonomous_state = 'PREPARE_PENALTY_OFFENSE'

            elif referee.command == RefereeCommand.PREPARE_PENALTY_THEM:
                DebugInterface().add_log(1, "Prepare penalty defense!")
                play_state.autonomous_state = 'PREPARE_PENALTY_DEFENSE'

            else:
                DebugInterface().add_log(1, "Unknown command... halting all the robots")
                play_state.autonomous_state = 'HALT'

            play_state.set_strategy(self._get_new_strategy(play_state.autonomous_state))


        self.last_ref_command = referee.command

    def _get_new_strategy(self, state):
        try:
            name = autonomousStrategies[state]
        except:
            name = autonomousStrategies['HALT']

        return self.ws.play_state.get_new_strategy(name)(self.ws.game_state)

    def _execute_strategy(self) -> None:
        """
        Éxecute la stratégie courante.

        :return: None
        """
        # Applique un stratégie par défault s'il n'en a pas (lors du démarage par exemple)
        if self.ws.play_state.current_strategy is None:
            self.ws.play_state.set_strategy(self.ws.play_state.
                                            get_new_strategy("HumanControl")
                                            (self.ws.game_state))
        # L'éxécution en tant que telle
        self.ws.play_state.current_ai_commands = \
            self.ws.play_state.current_strategy.exec()

    def _send_robots_status(self) -> None:
        """
        Envoie le status des robots (id, nom tactic + flag de status,
         nom action (phase tactic), target) par le debug interface.

        :return: None
        """
        states = self.ws.play_state.get_current_tactical_state()
        for state in states:
            player_id = state[0]
            tactic_name = state[1]
            action_name = state[2]
            target = (int(state[3].position.x), int(state[3].position.y))
            self.ws.debug_interface.send_robot_status(player_id,
                                                      tactic_name,
                                                      action_name,
                                                      target)

    def _send_auto_state(self) -> None:
        self.ws.debug_interface.send_auto_state(str(self.ws.game_state.game.referee.command.name),
                                                str(self.ws.game_state.game.referee.stage.name),
                                                str(self.ws.play_state.current_strategy),
                                                self.ws.play_state.autonomous_state,
                                                self.ws.play_state.autonomous_flag)

    def _send_books(self) -> None:
        """
        Envoie les livres de stratégies et de tactiques

        :return: None
        """
        cmd_tactics = {'strategy': self.ws.play_state.
                       strategy_book.get_strategies_name_list(),
                       'tactic': self.ws.play_state.tactic_book.
                       get_tactics_name_list(),
                       'action': ['None']}
        self.ws.debug_interface.send_books(cmd_tactics)
