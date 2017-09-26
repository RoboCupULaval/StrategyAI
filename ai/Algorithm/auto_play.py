from abc import abstractmethod, ABCMeta
from enum import IntEnum

from RULEngine.Game.Referee import RefereeCommand
from ai.Algorithm.IntelligentModule import IntelligentModule

from ai.Algorithm.evaluation_module import *

class AutoPlay(IntelligentModule, metaclass=ABCMeta):
    """
        Classe mère des modules de jeu automatique.
        Un module de jeu est un module intelligent servant à faire la sélection
        des stratégies en prenant en compte différents aspects du jeu, notamment le referee
        et la position des robots et de la balle.
    """
    def __init__(self, worldstate):
        super().__init__(worldstate)
        self.selected_strategy = None
        self.current_state = None
        self.next_state = None
        self.last_state = None

    def get_selected_strategy(self):
        return self.selected_strategy

    @property
    def info(self):
        return {
            "selected_strategy": str(self.selected_strategy),
            "current_state": str(self.current_state)
        }

    @abstractmethod
    def update(self, available_players_changed: bool):
        """ Effectue la mise à jour du module """
        pass

    @abstractmethod
    def str(self):
        """
            La représentation en string d'un module intelligent devrait
            permettre de facilement envoyer son information dans un fichier de
            log.
        """

class SimpleAutoPlayState(IntEnum):
    HALT = 0
    STOP = 1
    GOAL_US = 2
    GOAL_THEM = 3
    BALL_PLACEMENT_THEM = 4
    BALL_PLACEMENT_US = 5
    NORMAL_OFFENSE = 6
    NORMAL_DEFENSE = 7
    TIMEOUT = 8
    PREPARE_KICKOFF_OFFENSE = 9
    PREPARE_KICKOFF_DEFENSE = 10
    OFFENSE_KICKOFF = 11
    DEFENSE_KICKOFF = 12
    PREPARE_PENALTY_OFFENSE = 13
    PREPARE_PENALTY_DEFENSE = 14
    OFFENSE_PENALTY = 15
    DEFENSE_PENALTY = 16
    DIRECT_FREE_OFFENSE = 17
    DIRECT_FREE_DEFENSE = 18
    INDIRECT_FREE_OFFENSE = 19
    INDIRECT_FREE_DEFENSE = 20
        
class SimpleAutoPlay(AutoPlay):
    """
        Classe simple implémentant la sélection de stratégies.
    """
    def __init__(self, worldstate):
        super().__init__(worldstate)
        self.last_ref_command = RefereeCommand.HALT
        
    def update(self, available_players_changed: bool):
        self.next_state = self._select_next_state()

        if self.next_state is None:
            self.next_state = SimpleAutoPlayState.HALT
            self.selected_strategy = self._get_new_strategy(self.next_state)

        elif self.next_state != self.current_state or available_players_changed:
            self.selected_strategy = self._get_new_strategy(self.next_state)

        self.current_state = self.next_state

        self.ws.play_state.set_strategy(self.selected_strategy)
    
    def str(self):
        pass

    def _analyse_game(self):
        accepted_states = [
            SimpleAutoPlayState.OFFENSE_KICKOFF,
            SimpleAutoPlayState.DEFENSE_KICKOFF,
            SimpleAutoPlayState.OFFENSE_PENALTY,
            SimpleAutoPlayState.DEFENSE_PENALTY,
            SimpleAutoPlayState.DIRECT_FREE_DEFENSE,
            SimpleAutoPlayState.INDIRECT_FREE_DEFENSE
        ]
        if self.current_state in accepted_states and not is_ball_moving(300):
            return self.current_state
        if is_ball_our_side():
            return SimpleAutoPlayState.NORMAL_DEFENSE
        else:
            return SimpleAutoPlayState.NORMAL_OFFENSE

    def _normal_start(self):
        return {
            RefereeCommand.PREPARE_KICKOFF_US: SimpleAutoPlayState.OFFENSE_KICKOFF,
            RefereeCommand.PREPARE_KICKOFF_THEM: SimpleAutoPlayState.DEFENSE_KICKOFF,
            RefereeCommand.PREPARE_PENALTY_US: SimpleAutoPlayState.OFFENSE_PENALTY,
            RefereeCommand.PREPARE_PENALTY_THEM: SimpleAutoPlayState.DEFENSE_PENALTY,
            RefereeCommand.NORMAL_START: self._analyse_game()
        }.get(self.last_ref_command, RefereeCommand.NORMAL_START)

    def _select_next_state(self):
        referee = self.ws.game_state.game.referee
        next_state = self.current_state
        # On command change
        if self.last_ref_command != referee.command:
            next_state = {
                RefereeCommand.HALT: SimpleAutoPlayState.HALT,

                RefereeCommand.STOP: SimpleAutoPlayState.STOP,
                RefereeCommand.GOAL_US: self.current_state,
                RefereeCommand.GOAL_THEM: self.current_state,
                RefereeCommand.BALL_PLACEMENT_THEM: SimpleAutoPlayState.STOP,

                RefereeCommand.BALL_PLACEMENT_US: SimpleAutoPlayState.HALT, #TODO send ball new position to strategy...

                RefereeCommand.FORCE_START: self._analyse_game(),
                RefereeCommand.NORMAL_START: self._normal_start(),

                RefereeCommand.TIMEOUT_THEM: SimpleAutoPlayState.TIMEOUT,
                RefereeCommand.TIMEOUT_US: SimpleAutoPlayState.TIMEOUT,

                RefereeCommand.PREPARE_KICKOFF_US: SimpleAutoPlayState.PREPARE_KICKOFF_OFFENSE,
                RefereeCommand.PREPARE_KICKOFF_THEM: SimpleAutoPlayState.PREPARE_KICKOFF_DEFENSE,
                RefereeCommand.PREPARE_PENALTY_US: SimpleAutoPlayState.PREPARE_PENALTY_OFFENSE,
                RefereeCommand.PREPARE_PENALTY_THEM: SimpleAutoPlayState.PREPARE_PENALTY_DEFENSE,

                RefereeCommand.DIRECT_FREE_US: SimpleAutoPlayState.DIRECT_FREE_OFFENSE,
                RefereeCommand.DIRECT_FREE_THEM: SimpleAutoPlayState.DIRECT_FREE_DEFENSE,
                RefereeCommand.INDIRECT_FREE_US: SimpleAutoPlayState.INDIRECT_FREE_OFFENSE,
                RefereeCommand.INDIRECT_FREE_THEM: SimpleAutoPlayState.INDIRECT_FREE_DEFENSE

            }.get(referee.command, RefereeCommand.HALT)

        # During the game
        elif referee.command == RefereeCommand.FORCE_START or\
            referee.command == RefereeCommand.NORMAL_START:
            next_state = self._analyse_game()

        self.last_ref_command = referee.command
        return next_state

    def _get_new_strategy(self, state):
        name = self._get_strategy_name(state)
        return self.ws.play_state.get_new_strategy(name)(self.ws.game_state)

    def _get_strategy_name(self, state):
        return {
            # Robots must be stopped
            SimpleAutoPlayState.HALT: 'DoNothing',

            # Robots must stay 50 cm from the ball
            SimpleAutoPlayState.STOP: 'StayAway',
            SimpleAutoPlayState.GOAL_US: 'StayAway',
            SimpleAutoPlayState.GOAL_THEM: 'StayAway',
            SimpleAutoPlayState.BALL_PLACEMENT_THEM: 'StayAway',

            # Place the ball to the designated position
            SimpleAutoPlayState.BALL_PLACEMENT_US: 'DoNothing',

            SimpleAutoPlayState.NORMAL_OFFENSE: 'Offense',
            SimpleAutoPlayState.NORMAL_DEFENSE: 'DefenseWall',

            SimpleAutoPlayState.TIMEOUT: 'DoNothing',

            # Kickoff
            SimpleAutoPlayState.PREPARE_KICKOFF_OFFENSE: 'PrepareKickOffOffense',
            SimpleAutoPlayState.PREPARE_KICKOFF_DEFENSE: 'PrepareKickOffDefense',
            SimpleAutoPlayState.OFFENSE_KICKOFF: 'OffenseKickOff',
            SimpleAutoPlayState.DEFENSE_KICKOFF: 'DoNothing',

            # Penalty
            SimpleAutoPlayState.PREPARE_PENALTY_OFFENSE: 'PreparePenaltyOffense',
            SimpleAutoPlayState.PREPARE_PENALTY_DEFENSE: 'PreparePenaltyDefense',
            SimpleAutoPlayState.OFFENSE_PENALTY: 'PenaltyOffense',
            SimpleAutoPlayState.DEFENSE_PENALTY: 'PenaltyDefense',

            # Freekicks
            SimpleAutoPlayState.DIRECT_FREE_DEFENSE: 'DefenseWallNoKick',
            SimpleAutoPlayState.DIRECT_FREE_OFFENSE: 'DirectFreeKick',
            SimpleAutoPlayState.INDIRECT_FREE_DEFENSE: 'DefenseWallNoKick',
            SimpleAutoPlayState.INDIRECT_FREE_OFFENSE: 'IndirectFreeKick'

        }.get(state, SimpleAutoPlayState.HALT)