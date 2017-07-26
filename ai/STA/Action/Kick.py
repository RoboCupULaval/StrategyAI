# Under MIT license, see LICENSE.txt

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose

from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType, AIControlLoopType


class Kick(Action):

    def __init__(self, game_state: GameState, player: OurPlayer, force: [int, float]=5, target: Pose=Pose()):
        """
            :param game_state: Current state of the game
            :param player: Instance of the player
            :param p_force: Kick force [0, 10]
        """
        # TODO check the force not used by the new interface! MGL 2017/05/23
        Action.__init__(self, game_state, player)
        assert(isinstance(force, (int, float)))
        self.force = force
        self.target = target

    def exec(self):
        if self.target is None:
            new_position = self.player.pose.position
            orientation = self.player.pose.orientation
        else:
            new_position = self.game_state.get_ball_position()
            orientation = (self.target.position - ball_position).angle()

        cmd_params = {"pose_goal": Pose(new_position, orientation),
                      "kick": True,
                      "pathfinder_on": True,
                      "kick_strength": self.force,
                      "cruise_speed": 0,
                      "end_speed": 0}

        return AICommand(self.player, AICommandType.MOVE, **cmd_params)
