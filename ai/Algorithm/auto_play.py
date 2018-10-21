import logging
from abc import abstractmethod, ABCMeta
from enum import IntEnum

from Util.constant import IN_PLAY_MIN_DISTANCE
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
            "current_state": self.current_state.name if self.current_state is not None else str(self.current_state)
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
    NOT_ENOUGH_PLAYER = 21


class SimpleAutoPlay(AutoPlay):
    """
        Classe simple implémentant la sélection de stratégies.
    """

    NORMAL_STATE = [
        SimpleAutoPlayState.NORMAL_OFFENSE,
        SimpleAutoPlayState.NORMAL_DEFENSE
    ]

    FREE_KICK_STATE = [SimpleAutoPlayState.DIRECT_FREE_DEFENSE,
                       SimpleAutoPlayState.DIRECT_FREE_OFFENSE,
                       SimpleAutoPlayState.INDIRECT_FREE_DEFENSE,
                       SimpleAutoPlayState.INDIRECT_FREE_OFFENSE]

    KICKOFF_STATE = [SimpleAutoPlayState.OFFENSE_KICKOFF,
                       SimpleAutoPlayState.DEFENSE_KICKOFF]

    MINIMUM_NB_PLAYER = 3

    def __init__(self, play_state: PlayState):
        super().__init__(play_state)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.last_ref_state = RefereeCommand.HALT
        self.prev_nb_player = None
        self.start_state_ball_pos = None

    # TODO: Check if role assignment works well enough, so we don't need available_players_changed
    def update(self, ref_state: RefereeState, available_players_changed=False):
        self.play_state.game_state.last_ref_state = ref_state
        self.next_state = self._select_next_state(ref_state)

        if self.next_state is None:
            self.next_state = SimpleAutoPlayState.HALT
            self.play_state.current_strategy = SimpleAutoPlay._state_to_strategy_name(self.next_state)

        elif self.next_state != self.current_state or available_players_changed:
            self.logger.info("Switching to auto play state {}".format(self.next_state.name))
            self.play_state.current_strategy = SimpleAutoPlay._state_to_strategy_name(self.next_state)

        self.current_state = self.next_state
    
    def str(self):
        pass

    def _select_next_state(self, ref_state: RefereeState):

        # During the game
        next_state = self._exec_state()

        nb_player = len(GameState().our_team.available_players)
        if nb_player < self.MINIMUM_NB_PLAYER and ref_state.command != RefereeCommand.HALT:
            if self.prev_nb_player is None or nb_player != self.prev_nb_player:
                self.logger.warning("Not enough player to play. We have {} players and the minimum is {} "
                                    .format(nb_player, self.MINIMUM_NB_PLAYER))
            next_state = SimpleAutoPlayState.NOT_ENOUGH_PLAYER
        # Number of player change or On command change
        elif (self.prev_nb_player is not None and self.prev_nb_player < self.MINIMUM_NB_PLAYER <= nb_player)\
                or self.last_ref_state != ref_state.command:
            self.logger.info("Received referee state {}".format(ref_state.command.name))

            next_state = self._on_ref_state_change(ref_state.command)

        self.prev_nb_player = nb_player

        self.last_ref_state = ref_state.command
        return next_state

    @staticmethod
    def _state_to_strategy_name(state):
        return {
            # Robots must be stopped
            SimpleAutoPlayState.HALT: 'DoNothing',

            # Robots must stay 50 cm from the ball
            SimpleAutoPlayState.STOP: 'SmartStop',
            SimpleAutoPlayState.GOAL_US: 'IndianaJones',
            SimpleAutoPlayState.GOAL_THEM: 'StayAway',

            SimpleAutoPlayState.NORMAL_OFFENSE: 'Offense',
            SimpleAutoPlayState.NORMAL_DEFENSE: 'DefenseWall',

            SimpleAutoPlayState.TIMEOUT: 'DoNothing',

            # Kickoff
            SimpleAutoPlayState.PREPARE_KICKOFF_OFFENSE: 'PrepareKickOffOffense',
            SimpleAutoPlayState.PREPARE_KICKOFF_DEFENSE: 'PrepareKickOffDefense',
            SimpleAutoPlayState.OFFENSE_KICKOFF: 'OffenseKickOff',
            SimpleAutoPlayState.DEFENSE_KICKOFF: 'PrepareKickOffDefense',

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
            SimpleAutoPlayState.BALL_PLACEMENT_US: 'BallPlacement',

            # When not enough player:
            SimpleAutoPlayState.NOT_ENOUGH_PLAYER: 'DoNothing'

        }.get(state, 'DoNothing')

    def _on_ref_state_change(self, ref_cmd: RefereeCommand):
        self.start_state_ball_pos = GameState().ball_position
        return {
            RefereeCommand.HALT: SimpleAutoPlayState.HALT,

            RefereeCommand.STOP: SimpleAutoPlayState.STOP,
            RefereeCommand.GOAL_US: self.current_state,
            RefereeCommand.GOAL_THEM: self.current_state,

            RefereeCommand.FORCE_START: self._decide_between_normal_play(),
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

        }.get(ref_cmd, SimpleAutoPlayState.HALT)

    def _normal_start(self):
        return {
            RefereeCommand.PREPARE_KICKOFF_US: SimpleAutoPlayState.OFFENSE_KICKOFF,
            RefereeCommand.PREPARE_KICKOFF_THEM: SimpleAutoPlayState.DEFENSE_KICKOFF,
            RefereeCommand.PREPARE_PENALTY_US: SimpleAutoPlayState.OFFENSE_PENALTY,
            RefereeCommand.PREPARE_PENALTY_THEM: SimpleAutoPlayState.DEFENSE_PENALTY,
            RefereeCommand.NORMAL_START: self._decide_between_normal_play()
        }.get(self.last_ref_state, SimpleAutoPlayState.NORMAL_DEFENSE)

    def _decide_between_normal_play(self):
        if is_ball_our_side():
            return SimpleAutoPlayState.NORMAL_DEFENSE
        else:
            return SimpleAutoPlayState.NORMAL_OFFENSE

    def _is_ball_in_play(self):
        if self.current_state in [SimpleAutoPlayState.STOP, SimpleAutoPlayState.HALT]:
            return False
        return (self.start_state_ball_pos - GameState().ball_position).norm > IN_PLAY_MIN_DISTANCE

    def _exec_state(self):
        # We use the ball's mobility for detecting a kick and change state
        if self.current_state in self.NORMAL_STATE and GameState().ball.is_immobile():
            return self._decide_between_normal_play()
        elif self.current_state in self.FREE_KICK_STATE and self._is_ball_in_play():
            return self._decide_between_normal_play()
        elif self.current_state in self.KICKOFF_STATE and self._is_ball_in_play():
            return self._decide_between_normal_play()

        return self.current_state