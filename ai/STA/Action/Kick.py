# Under MIT license, see LICENSE.txt


from Util import Pose, AICommand
from ai.GameDomainObjects import Player
from ai.STA.Action import Action
from ai.states.game_state import GameState


class Kick(Action):

    def __init__(self, game_state: GameState, player: Player, force: [int, float], target: Pose=Pose(), target_speed=0,
                 cruise_speed=0.1):
        """
            :param game_state: Current state of the game
            :param player: Instance of the player
            :param p_force: Kick force [0, 10]
        """
        Action.__init__(self, game_state, player)
        assert(isinstance(force, (int, float)))
        self.force = force
        self.target = target
        self.target_speed = target_speed

    def exec(self):
        """
        Execute the kick command
        :return: Un AIcommand
        """
        if self.target is not None:
            ball_position = self.game_state.ball_position
            orientation = (self.target.position - self.player.pose.position).angle
        else:
            ball_position = self.player.pose.position
            orientation = self.player.pose.orientation

        cmd_params = {"target": Pose(ball_position, orientation),
                      "kick_type": 1,
                      "kick_force": self.force,
                      "cruise_speed": 0.1,
                      "charge_kick": True,
                      "target_speed": self.target_speed,
                      "ball_collision": False}

        return AICommand(self.player.id, **cmd_params)
