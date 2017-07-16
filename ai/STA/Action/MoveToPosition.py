# Under MIT license, see LICENSE.txt
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType
from ai.states.game_state import GameState


class MoveToPosition(Action):

    def __init__(self, game_state: GameState, player: OurPlayer, destination: Pose, pathfinder_on=True, cruise_speed: [int, float]=1,  collision_ball=False):
        """
            :param game_state: Current state of the game.
            :param player: Instance of the player
            :param p_destination: destination to reach
            :param pathfinder_on:
            :param cruise_speed
        """
        Action.__init__(self, game_state, player)
        assert isinstance(destination, Pose)
        assert isinstance(cruise_speed, (int, float))
        self.destination = destination
        self.pathfinder_on = pathfinder_on
        self.cruise_speed = cruise_speed
        self.collision_ball = collision_ball

    def exec(self):

        return AICommand(self.player,
                         AICommandType.MOVE,
                         pose_goal=self.destination,
                         pathfinder_on=self.pathfinder_on,
                         cruise_speed=self.cruise_speed,
                         collision_ball=self.collision_ball)
