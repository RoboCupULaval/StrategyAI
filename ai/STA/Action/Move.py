# Under MIT license, see LICENSE.txt
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.SpeedPose import SpeedPose
from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType, AIControlLoopType


class Move(Action):

    def __init__(self, game_state: GameState, player: OurPlayer, velocity: SpeedPose):
        """
            :param game_state: Current state of the game.
            :param player: Instance of the player
            :param velocity: Velocity vector of the player
        """
        Action.__init__(self, game_state, player)
        assert isinstance(velocity, Pose)
        self.velocity = velocity

    def exec(self):

        cmd_params = {"pose_goal": self.velocity, "control_loop_type": AIControlLoopType.SPEED}
        return AICommand(self.player, AICommandType.MOVE, **cmd_params)
