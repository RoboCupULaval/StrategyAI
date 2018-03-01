
from RULEngine.controllers.controller_base_class import ControllerBaseClass
from RULEngine.robot import Robot

from Util import Pose
from Util.PID import PID
from Util.geometry import wrap_to_pi, rotate


class RealPositionController(ControllerBaseClass):

    def __init__(self, control_setting):
        self.controllers = {'x': PID(**control_setting['translation']),
                            'y': PID(**control_setting['translation']),
                            'orientation': PID(**control_setting['rotation'], wrap_error=True)}

    def execute(self, robot: Robot):
        pose = robot.pose
        target = Pose(robot.path.points[1], robot.target_orientation)

        pos_error = target.position - pose.position
        orientation_error = wrap_to_pi(target.orientation - pose.orientation)

        command = Pose.from_values(self.controllers['x'].execute(pos_error.x),
                                   self.controllers['y'].execute(pos_error.y),
                                   self.controllers['orientation'].execute(orientation_error))

        command.position = rotate(command.position, -pose.orientation)

        # Limit max linear speed
        command.position /= max(1, command.norm / robot.max_linear_speed)

        return command

    def reset(self):
        for controller in self.controllers.values():
            controller.reset()


class GrSimPositionController(RealPositionController):
    pass
