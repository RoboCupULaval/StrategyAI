
from RULEngine.regulators.PID import PID
from RULEngine.regulators.regulator_base_class import RegulatorBaseClass
from RULEngine.robot import Robot, MAX_LINEAR_SPEED
from Util import Pose
from Util.geometry import wrap_to_pi, rotate


class RealPositionRegulator(RegulatorBaseClass):

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
        command.position /= max(1, command.norm / MAX_LINEAR_SPEED)

        return command

    def reset(self):
        for controller in self.controllers.values():
            controller.reset()


class GrSimPositionRegulator(RealPositionRegulator):
    pass
