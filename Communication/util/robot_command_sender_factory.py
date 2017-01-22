from RULEngine.Communication.sender.grsim_command_sender import GrSimCommandSender
from RULEngine.Communication.sender.serial_command_sender import SerialCommandSender, SerialType, SERIAL_DISABLED
from RULEngine.Communication.util.serial_protocol import MCUVersion


class RobotCommandSenderFactory(object):

    @staticmethod
    def get_sender(type_of_connection, mcu_version=MCUVersion.STM32F407):
        if type_of_connection == SERIAL_DISABLED:
            return GrSimCommandSender("127.0.0.1", 20011)
        elif type_of_connection in SerialType:
            return SerialCommandSender(serial_type=type_of_connection, mcu_version=mcu_version)
        else:
            raise TypeError("Tentative de création d'un RobotCommandSender de "
                            "mauvais type.")
