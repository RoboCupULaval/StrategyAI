from Engine.Communication.sender.fake_sender import FakeSender
from Engine.Communication.sender.grsim_command_sender import GrSimCommandSender
from Engine.Communication.sender.serial_command_sender import SerialCommandSender
from config.config import Config


class RobotCommandSender:

    def __new__(cls):

        connection_infos = {'sim': Config()['COMMUNICATION']['grsim_info']}

        available_sender = {'disabled': FakeSender,
                            'sim':      GrSimCommandSender,
                            'serial':   SerialCommandSender}

        sender_type = Config()['COMMUNICATION']['type']

        sender_class = available_sender.get(sender_type, None)
        connection_info = connection_infos.get(sender_type, None)

        if sender_class is not None:
            instance = sender_class(connection_info)
        else:
            raise TypeError('{} is not a valid type for a RobotCommandSender.'.format(sender_type))

        return instance
