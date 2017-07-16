from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose
from RULEngine.Util.SpeedPose import SpeedPose
from RULEngine.Util.Position import Position
from RULEngine.Util.kalman_filter.friend_kalman_filter import FriendKalmanFilter
from ai.Util.pathfinder_history import PathfinderHistory


class OurPlayer(Player):
    max_speed = 2
    max_angular_speed = 3.14
    max_acc = 1.5

    def __init__(self, team, id: int):
        super().__init__(team=team, id=id)
#        self.debug_interface = DebugInterface()
        self.kf = FriendKalmanFilter()
        self.ai_command = None
        self.pid = None  # for the moment
        self.in_play = False
        self.update = self._friend_kalman_update
        self.pathfinder_history = PathfinderHistory()

    def _friend_kalman_update(self, poses, delta):
        ret = self.kf.filter(poses, self.cmd, delta)
        self.pose = Pose(Position(ret[0], ret[1]), ret[4])
        self.velocity = SpeedPose(Position(ret[2], ret[3]), ret[5])
    #     self.display_player_pose(self.pose)
    #
    # def display_player_pose(self, pose):
    #
    #     self.debug_interface.add_circle(center=(pose[0], pose[1]), radius=ROBOT_RADIUS,
    #                                     color=COLOR_ID_MAP[2], timeout=0.1)

        # def add_circle(self, center, radius):
        #     data = {'center': center,
        #             'radius': radius,
        #             'color': CYAN.repr(),
        #             'is_fill': True,
        #             'timeout': 0}
        #     circle = DebugCommand(3003, data)
        #     self.debug_state.append(circle)

    def set_command(self):
        if self.ai_command.speed is not None:
            self.cmd = [self.ai_command.speed.position.x,
                        self.ai_command.speed.position.y,
                        self.ai_command.speed.orientation]
        else:
            self.cmd = None

