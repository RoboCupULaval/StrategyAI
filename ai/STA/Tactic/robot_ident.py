# Under MIT license, see LICENSE.txt
import csv
import math as m
import time

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Move import Move
from ai.Util.ai_command import AICommandType, AICommand, AIControlLoopType
from ai.Util.joystick.joystick import RobotJoystick
from .Tactic import Tactic
from . tactic_constants import Flags


class RobotIdent(Tactic):
    def __init__(self, p_game_state, player_id, target, args):
        super().__init__(p_game_state, player_id, target, args)
        self.target = target
        self.status_flag = Flags.INIT

        self.cmd_filename = str(args[0])
        self.output_filename = str(args[1])

        self.cmd_id = 0
        self.start_time = 0

        self.commands = []
        with open(self.cmd_filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                cmd = tuple(float(i) for i in row)
                self.commands.append(cmd)

        with open(self.output_filename, 'w') as f:
            f.write('time,cmd_vx,px,vx,cmd_vy,py,vy,cmd_vt,pt,vt\n')



    def exec(self):
        if self.status_flag is not Flags.FAILURE and self.cmd_id < len(self.commands) - 1:
            self.status_flag = Flags.WIP

            # Creating speed pose
            cmd_vx, cmd_vy, cmd_vt = self.commands[self.cmd_id]
            speed_pose = Pose(Position(cmd_vx, cmd_vy), cmd_vt)
            self.cmd_id = self.cmd_id + 1

            # Saving data
            px = self.game_state.get_player(self.player_id).pose.position.x / 1000.0
            vx = self.game_state.get_player(self.player_id).velocity[0]
            py = self.game_state.get_player(self.player_id).pose.position.y / 1000.0
            vy = self.game_state.get_player(self.player_id).velocity[1]
            pt = self.game_state.get_player(self.player_id).pose.orientation
            vt = self.game_state.get_player(self.player_id).velocity[2]

            if self.cmd_id == 0:
                self.start_time = time.time()
            t = time.time() - self.start_time

            with open(self.output_filename, 'a') as f:
                f.write('{},{},{},{},{},{},{},{},{},{}\n'.format(t, cmd_vx, px, vx, cmd_vy, py, vy, cmd_vt, pt, vt))

            next_action = AICommand(self.player_id, AICommandType.MOVE,
                             **{"pose_goal": speed_pose, "control_loop_type": AIControlLoopType.OPEN})
        else:
            next_action = Idle(self.game_state, self.player_id).exec()

        return next_action

    def halt(self):
        return super(RobotIdent, self).halt()
