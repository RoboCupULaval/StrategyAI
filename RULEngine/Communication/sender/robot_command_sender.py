from RULEngine.Communication.sender.fake_sender import FakeSender
from RULEngine.Communication.sender.grsim_command_sender import GrSimCommandSender
from RULEngine.Communication.sender.serial_command_sender import SerialCommandSender
from config.config_service import ConfigService


class RobotCommandSender:

    def __new__(cls, connection_info, queue, stop_event):

        available_sender = {'disabled': FakeSender,
                            'sim':      GrSimCommandSender,
                            'serial':   SerialCommandSender}

        sender_type = ConfigService().config_dict['COMMUNICATION']['type']

        sender_class = available_sender.get(sender_type, None)

        if sender_class is not None:
            instance = sender_class(connection_info, queue, stop_event)
        else:
            raise TypeError('{} is not a valid type for a RobotCommandSender.'.format(sender_type))

        return instance
