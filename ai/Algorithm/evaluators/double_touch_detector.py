import logging

from Util.constant import IN_PLAY_MIN_DISTANCE, ROBOT_RADIUS


def find_players_touching_the_ball(game_state):
    REASONABLE_OFFSET = 30
    ball_pos = game_state.ball.position
    players = list(game_state.our_team.available_players.values()) + \
              list(game_state.enemy_team.available_players.values())

    # We might never detect the touching player, but we might detect the ball acceleration
    # TODO check behind the ball, instead of in a circle
    offset = REASONABLE_OFFSET * (1 + game_state.ball.velocity.norm / 100)
    for p in players:
        if (p.position - ball_pos).norm <= ROBOT_RADIUS + offset:
            yield p


class DoubleTouchDetector(object):
    """ Basic state machine to track which player can not kick the ball.
        It must be enable by the autoplay"""
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self._state = self._disabled
        self._our_kicker = None
        self._ball_position_at_start = None
        self._ban_players = []

    def update(self, game_state):
        self._state(game_state)

    def enable(self):
        self.logger.info("Enable double touch detector")
        self._state = self._waiting_for_touch

    def disable(self):
        self.logger.info("Disabling double touch detector")
        self._state = self._disabled

    @property
    def ban_players(self):
        return self._ban_players

    # All of the following method are states
    def _disabled(self, _):
        self._our_kicker = None
        self._ball_position_at_start = None
        self._ban_players = []

    def _waiting_for_touch(self, game_state):
        for p in find_players_touching_the_ball(game_state):
            if p in game_state.our_team.available_players.values():
                self.logger.info(f"Our Player {p} has touch the ball.")
                self._our_kicker = p
                self._state = self._waiting_for_kicker_to_kick
            else:  # A enemy touch the ball, no double touch
                self.logger.info(f"The enemy Player {p} has touch the ball.")
                self.disable()
            return

    def _waiting_for_kicker_to_kick(self, game_state):
        if self._ball_position_at_start is None:
            self._ball_position_at_start = game_state.ball.position.copy()

        if (self._ball_position_at_start - game_state.ball.position).norm > IN_PLAY_MIN_DISTANCE:
            self.logger.info(f"Our kicker {self._our_kicker} has move the ball too much, it can not touch it again.")
            self._ban_players = [self._our_kicker]
            self._state = self._waiting_for_another_player_to_touch_ball
        else:  # Another player might touch the ball while we are kicking
            self._waiting_for_another_player_to_touch_ball(game_state)

    def _waiting_for_another_player_to_touch_ball(self, game_state):
        for p in find_players_touching_the_ball(game_state):
            if p != self._our_kicker:
                self.logger.info(f"Another player {p} has touch the ball, double touch adverted.")
                self.disable()
                return
