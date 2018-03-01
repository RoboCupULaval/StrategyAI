
from RULEngine.controllers.position_controllers import GrSimPositionController, RealPositionController
from RULEngine.controllers.velocity_controllers import GrSimVelocityController, RealVelocityController
from config.config_service import ConfigService


class ControllerFactory:
    available_controllers = None
    controllers_settings = None

    def __new__(cls):

        controller_type = ConfigService().config_dict['COMMUNICATION']['type']

        controller_class = cls.available_controllers.get(controller_type, None)
        controller_setting = cls.controllers_settings.get(controller_type, None)

        if not controller_class:
            raise TypeError('{} is not a valid type for a {} controller.'.format(controller_type, cls.__name__))
        elif not controller_setting:
            raise TypeError('{} is not a valid settings for a {} controller.'.format(controller_type, cls.__name__))

        return controller_class(controller_setting)


class PositionController(ControllerFactory):
    available_controllers = {'sim': GrSimPositionController,
                             'serial': RealPositionController}

    controllers_settings = {
        'sim': {'translation': {'kp': 1, 'ki': 0.1, 'kd': 0},
                'rotation': {'kp': .75, 'ki': 0.15, 'kd': 0}},

        'serial': {'translation': {'kp': .01, 'ki': 0.0, 'kd': 0},
                   'rotation': {'kp': 0.5, 'ki': 0.02, 'kd': 0.0}}
    }


class VelocityController(ControllerFactory):
    available_controllers = {'sim': GrSimVelocityController,
                             'serial': RealVelocityController}

    controllers_settings = {
        'sim': {'translation': {'kp': 1, 'ki': 0.1, 'kd': 0},
                'rotation': {'kp': .75, 'ki': 0.15, 'kd': 0}},

        'serial': {'translation': {'kp': .01, 'ki': 0.0, 'kd': 0},
                   'rotation': {'kp': 0.5, 'ki': 0.02, 'kd': 0.0}}
    }