from Engine.regulators.PID import PID
from Engine.regulators.regulator_base_class import RegulatorBaseClass
from Engine.robot import Robot, MAX_LINEAR_SPEED, MAX_ANGULAR_SPEED
from Util import Pose


class RealPositionRegulator(RegulatorBaseClass):

    settings = {
        'translation': {'kp': 2, 'ki': 0.1, 'kd': 0},
        'rotation': {'kp': 8, 'ki': 0, 'kd': 1}
    }

    def __init__(self):
        self.controllers = {'x': PID(**self.settings['translation']),
                            'y': PID(**self.settings['translation']),
                            'orientation': PID(**self.settings['rotation'], signed_error=True, deadzone=0.10)}

    def execute(self, robot: Robot, dt: float):

        pos_error = robot.position_error
        orientation_error = robot.orientation_error

        command = Pose.from_values(self.controllers['x'].execute(pos_error.x),
                                   self.controllers['y'].execute(pos_error.y),
                                   self.controllers['orientation'].execute(orientation_error))

        # Limit max linear speed
        command.position /= max(1.0, command.norm / MAX_LINEAR_SPEED)
        command.orientation /= max(1.0, abs(command.orientation) / MAX_ANGULAR_SPEED)
        return command

    def reset(self):
        for controller in self.controllers.values():
            controller.reset()


class GrSimPositionRegulator(RealPositionRegulator):

    settings = {
        'translation': {'kp': 2, 'ki': 0.1, 'kd': 0.01},
        'rotation': {'kp': 1, 'ki': 0.02, 'kd': 0.0}
    }