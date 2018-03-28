
from Engine.regulators.PID import PID
from Engine.regulators.regulator_base_class import RegulatorBaseClass
from Engine.robot import Robot, MAX_LINEAR_SPEED, MAX_ANGULAR_SPEED
from Util import Pose
from Util.geometry import wrap_to_pi, rotate


class RealPositionRegulator(RegulatorBaseClass):

    settings = {
        'translation': {'kp': 2, 'ki': 0.1, 'kd': 0},
        'rotation': {'kp': 2, 'ki': 0.5, 'kd': 0}
    }

    def __init__(self):
        self.controllers = {'x': PID(**self.settings['translation']),
                            'y': PID(**self.settings['translation']),
                            'orientation': PID(**self.settings['rotation'], wrap_error=True)}

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
        command.position /= max(1, command.norm / MAX_LINEAR_SPEED)
        command.orientation /= max(1, abs(command.orientation) / MAX_ANGULAR_SPEED)
        return command

    def reset(self):
        for controller in self.controllers.values():
            controller.reset()


class GrSimPositionRegulator(RealPositionRegulator):

    settings = {
        'translation': {'kp': 2, 'ki': 0, 'kd': 0.01},
        'rotation': {'kp': 1, 'ki': 0.02, 'kd': 0.0}
    }
