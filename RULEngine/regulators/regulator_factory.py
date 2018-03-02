from RULEngine.regulators.position_regulators import GrSimPositionRegulator, RealPositionRegulator
from RULEngine.regulators.velocity_regulators import GrSimVelocityController, RealVelocityController
from config.config_service import ConfigService


class RegulatorFactory:
    available_regulators = None

    def __new__(cls):
        regulator_type = ConfigService().config_dict['COMMUNICATION']['type']
        regulator_class = cls.available_regulators.get(regulator_type, None)

        if not regulator_class:
            raise TypeError('{} is not a valid type for a {} regulator.'.format(regulator_type, cls.__name__))

        return regulator_class()


class PositionRegulator(RegulatorFactory):
    available_regulators = {'sim': GrSimPositionRegulator,
                            'serial': RealPositionRegulator}


class VelocityRegulator(RegulatorFactory):
    available_regulators = {'sim': GrSimVelocityController,
                            'serial': RealVelocityController}
