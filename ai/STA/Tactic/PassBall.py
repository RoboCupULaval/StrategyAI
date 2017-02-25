# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.Kick import Kick
from ai.STA.Action.Idle import Idle
from ai.Util.ball_possession import has_ball_facing_target, has_ball
from RULEngine.Util.kick import getRequiredKickForce
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.Position import Position

__author__ = 'RoboCupULaval'


class PassBall(Tactic):
    # TODO : vérifier que la balle a été bottée avant de retourner à halt
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: L'état courant du jeu.
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
        target_position : La position du robot qui reçoit la passe
    """

    def __init__(self, game_state, player_id, target_position):
        Tactic.__init__(self, game_state, player_id)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0
        assert isinstance(target_position, Position)
        # TODO : s'assurer de la target_position soit à l'intérieur du terrain

        self.current_state = self.kick_ball_towards_target
        self.next_state = self.kick_ball_towards_target
        self.player_id = player_id
        self.target_position = target_position

    def kick_ball_towards_target(self):
        print(str(self.player_id) + ": Kick")
        # check alignment before kicking
        if has_ball_facing_target(self.game_state, self.player_id, self.target_position):
            player_position = self.game_state.get_player_position(self.player_id)
            kick_force = getRequiredKickForce(player_position, self.target_position)

            kick_ball = Kick(self.game_state, self.player_id, kick_force)

            self.next_state = self.halt
            self.status_flag = Flags.SUCCESS
            print("kick")
            return kick_ball
        elif has_ball(self.game_state, self.player_id):
            print("needs to face target")
            self.next_state = self.halt
            self.status_flag = Flags.FAILURE
            return Idle(self.game_state, self.player_id)
        else:  # returns error, strategy goes back to GoGetBall
            print("kick failed")
            self.next_state = self.halt
            self.status_flag = Flags.FAILURE
            return Idle(self.game_state, self.player_id)
