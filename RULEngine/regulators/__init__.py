
from RULEngine.regulators.position_regulators import GrSimPositionRegulator, RealPositionRegulator
from RULEngine.regulators.velocity_regulators import GrSimVelocityController, RealVelocityController
from config.config_service import ConfigService


class RegulatorFactory:
    available_regulators = None
    regulators_settings = None

    def __new__(cls):

        regulator_type = ConfigService().config_dict['COMMUNICATION']['type']

        regulator_class = cls.available_regulators.get(regulator_type, None)
        regulator_setting = cls.regulators_settings.get(regulator_type, None)

        if not regulator_class:
            raise TypeError('{} is not a valid type for a {} regulator.'.format(regulator_type, cls.__name__))
        elif not regulator_setting:
            raise TypeError('{} is not a valid settings for a {} regulator.'.format(regulator_type, cls.__name__))

        return regulator_class(regulator_setting)


class PositionRegulator(RegulatorFactory):
    available_regulators = {'sim': GrSimPositionRegulator,
                            'serial': RealPositionRegulator}

    regulators_settings = {
        'sim': {'translation': {'kp': 1, 'ki': 0.1, 'kd': 0},
                'rotation': {'kp': .75, 'ki': 0.15, 'kd': 0}},

        'serial': {'translation': {'kp': .01, 'ki': 0.0, 'kd': 0},
                   'rotation': {'kp': 0.5, 'ki': 0.02, 'kd': 0.0}}
    }


class VelocityRegulator(RegulatorFactory):
    available_regulators = {'sim': GrSimVelocityController,
                            'serial': RealVelocityController}

    regulators_settings = {
        'sim': {'translation': {'kp': 1, 'ki': 0.1, 'kd': 0},
                'rotation': {'kp': .75, 'ki': 0.15, 'kd': 0}},

        'serial': {'translation': {'kp': .01, 'ki': 0.0, 'kd': 0},
                   'rotation': {'kp': 0.5, 'ki': 0.02, 'kd': 0.0}}
    }