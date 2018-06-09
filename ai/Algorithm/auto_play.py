import logging
from abc import abstractmethod, ABCMeta
from enum import IntEnum

from ai.Algorithm.IntelligentModule import IntelligentModule
from ai.Algorithm.evaluation_module import *
from ai.GameDomainObjects.referee_state import RefereeCommand, RefereeState
from ai.states.play_state import PlayState
from ai.states.game_state import GameState


class AutoPlay(IntelligentModule, metaclass=ABCMeta):
    """
        Classe mère des modules de jeu automatique.
        Un module de jeu est un module intelligent servant à faire la sélection
        des stratégies en prenant en compte différents aspects du jeu, notamment le referee
        et la position des robots et de la balle.
    """
    def __init__(self, play_state: PlayState):
        super().__init__()
        self.play_state = play_state
        self.selected_strategy = None
        self.current_state = None
        self.next_state = None
        self.last_state = None

    @property
    def info(self):
        return {
            "selected_strategy": str(self.play_state.current_strategy),
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

    FREE_KICK_COMMANDS = [RefereeCommand.DIRECT_FREE_US, RefereeCommand.INDIRECT_FREE_US,
                          RefereeCommand.DIRECT_FREE_THEM, RefereeCommand.INDIRECT_FREE_THEM]
    MINIMUM_NB_PLAYER = 3

    def __init__(self, play_state: PlayState):
        super().__init__(play_state)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.last_ref_state = RefereeCommand.HALT
        self.prev_nb_player = None

    # TODO: Check if role assignment works well enough, so we don't need available_players_changed
    def update(self, ref_state: RefereeState, available_players_changed=False):
        self.play_state.game_state.last_ref_state = ref_state
        self.next_state = self._select_next_state(ref_state)

        nb_player = len(GameState().our_team.available_players)
        if nb_player < self.MINIMUM_NB_PLAYER and ref_state.command != RefereeCommand.HALT:
            if self.prev_nb_player or nb_player != self.prev_nb_player:
                self.logger.warning("Not enough player to play. We have {} players and the minimum is {} "
                                    .format(nb_player, self.MINIMUM_NB_PLAYER))
            self.play_state.current_strategy = 'DoNothing'
        elif self.next_state is None:
            self.next_state = SimpleAutoPlayState.HALT
            self.play_state.current_strategy = SimpleAutoPlay._state_to_strategy_name(self.next_state)

        elif self.next_state != self.current_state or available_players_changed:
            self.play_state.current_strategy = SimpleAutoPlay._state_to_strategy_name(self.next_state)

        self.current_state = self.next_state
        self.prev_nb_player = nb_player
    
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
        if self.current_state in accepted_states and not GameState().ball.is_immobile():
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
        }.get(self.last_ref_state, RefereeCommand.NORMAL_START)

    def _select_next_state(self, ref_state: RefereeState):
        next_state = self.current_state

        # On command change
        if self.last_ref_state != ref_state.command:
            self.logger.info("Switching to referee state {}".format(ref_state.command.name))
            next_state = {
                RefereeCommand.HALT: SimpleAutoPlayState.HALT,

                RefereeCommand.STOP: SimpleAutoPlayState.STOP,
                RefereeCommand.GOAL_US: self.current_state,
                RefereeCommand.GOAL_THEM: self.current_state,

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
                RefereeCommand.INDIRECT_FREE_THEM: SimpleAutoPlayState.INDIRECT_FREE_DEFENSE,

                RefereeCommand.BALL_PLACEMENT_THEM: SimpleAutoPlayState.STOP,
                RefereeCommand.BALL_PLACEMENT_US: SimpleAutoPlayState.BALL_PLACEMENT_US,

            }.get(ref_state.command, RefereeCommand.HALT)

        # During the game
        elif ref_state.command == RefereeCommand.FORCE_START or ref_state.command == RefereeCommand.NORMAL_START:
            next_state = self._analyse_game()
        elif GameState().ball.is_mobile() and ref_state.command in self.FREE_KICK_COMMANDS:
            return SimpleAutoPlayState.NORMAL_OFFENSE

        self.last_ref_state = ref_state.command
        return next_state

    @staticmethod
    def _state_to_strategy_name(state):
        return {
            # Robots must be stopped
            SimpleAutoPlayState.HALT: 'DoNothing',

            # Robots must stay 50 cm from the ball
            SimpleAutoPlayState.STOP: 'StayAway',
            SimpleAutoPlayState.GOAL_US: 'StayAway',
            SimpleAutoPlayState.GOAL_THEM: 'StayAway',

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
            SimpleAutoPlayState.INDIRECT_FREE_OFFENSE: 'IndirectFreeKick',

            # Place the ball to the designated position
            SimpleAutoPlayState.BALL_PLACEMENT_US: 'BallPlacement'

        }.get(state, SimpleAutoPlayState.HALT)
