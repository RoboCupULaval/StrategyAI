from Engine.regulators.position_regulators import GrSimPositionRegulator, RealPositionRegulator
from Engine.regulators.velocity_regulators import GrSimVelocityController, RealVelocityController
from config.config import Config


class RegulatorFactory:
    available_regulators = None

    def __new__(cls):
        regulator_type = Config()['GAME']['type']
        regulator_class = cls.available_regulators.get(regulator_type, None)

        if not regulator_class:
            raise TypeError('{} is not a valid type for a {} regulator.'.format(regulator_type, cls.__name__))

        return regulator_class()


class PositionRegulator(RegulatorFactory):
    available_regulators = {'sim': GrSimPositionRegulator,
                            'real': RealPositionRegulator}


class VelocityRegulator(RegulatorFactory):
    available_regulators = {'sim': GrSimVelocityController,
                            'real': RealVelocityController}
