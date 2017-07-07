# Under MIT license, see LICENSE.txt

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.SpeedPose import SpeedPose
from RULEngine.Util.Pose import Pose

from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType, AIControlLoopType


class Kick(Action):

    def __init__(self, game_state: GameState, player: OurPlayer, p_force: [int, float], target: Pose=Pose()):
        """
            :param game_state: Current state of the game
            :param player: Instance of the player
            :param p_force: Kick force [0, 10]
        """
        # TODO check the force not used by the new interface! MGL 2017/05/23
        Action.__init__(self, game_state, player)
        assert(isinstance(p_force, (int, float)))
        self.force = p_force
        self.target = target

    def exec(self):
        """
        Execute the kick command
        :return: Un AIcommand
        """
        target = self.target.position
        player = self.player.pose.position
        player_to_target = target - player
        player_to_target = 0.3 * player_to_target.normalized()

        cmd_params = {"pose_goal": SpeedPose(player_to_target),
                      "control_loop_type": AIControlLoopType.SPEED,
                      "kick": True,
                      "kick_strength": self.force}
        return AICommand(self.player, AICommandType.MOVE, **cmd_params)
