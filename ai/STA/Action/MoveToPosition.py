# Under MIT license, see LICENSE.txt
from RULEngine.GameDomainObjects.player import Player
from Util.ai_command import AICommand
from Util.Pose import Pose
from ai.STA.Action.Action import Action
from ai.states.game_state import GameState


class MoveToPosition(Action):

    def __init__(self, game_state: GameState, player: Player,
                 destination: Pose,
                 pathfinder_on=True,
                 cruise_speed: [int, float]=1,
                 collision_ball=False,
                 charge_kick=False,
                 end_speed=0,
                 dribbler_on=False):

        Action.__init__(self, game_state, player)

        assert isinstance(destination, Pose)
        assert isinstance(cruise_speed, (int, float))

        self.destination = destination
        self.pathfinder_on = pathfinder_on
        self.cruise_speed = cruise_speed
        self.collision_ball = collision_ball
        self.charge_kick = charge_kick
        self.end_speed = end_speed
        self.dribbler_on = dribbler_on

    def exec(self):
        return AICommand(self.player.id, self.destination.to_dict())
