from Engine.Communication.sender.fake_sender import FakeSender
from Engine.Communication.sender.grsim_command_sender import GrSimCommandSender
from Engine.Communication.sender.serial_command_sender import SerialCommandSender
from config.config import Config


class RobotCommandSender:

    def __new__(cls):

        sender_type = Config()['COMMUNICATION']['type']

        if sender_type == 'grsim':
            connection_info = Config()['COMMUNICATION']['grsim_info']
        else:
            connection_info = None

        available_sender = {'disabled': FakeSender,
                            'grsim':    GrSimCommandSender,
                            'serial':   SerialCommandSender}

        sender_class = available_sender.get(sender_type, None)

        if sender_class is not None:
            instance = sender_class(connection_info)
        else:
            raise TypeError('{} is not a valid type for a RobotCommandSender.'.format(sender_type))

        return instance
