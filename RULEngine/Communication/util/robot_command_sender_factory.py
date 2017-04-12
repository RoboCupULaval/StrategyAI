from RULEngine.Communication.sender.grsim_command_sender import GrSimCommandSender
from RULEngine.Communication.sender.serial_command_sender import SerialCommandSender
from config.config_service import ConfigService


class RobotCommandSenderFactory(object):

    @staticmethod
    def get_sender():
        type_of_connection = ConfigService().config_dict["COMMUNICATION"]["type"]
        if type_of_connection == "sim":
            return GrSimCommandSender("127.0.0.1", 20011)
        elif type_of_connection == "serial":
            return SerialCommandSender()
        elif type_of_connection == "disabled":
            return lambda *args: None
        else:
            raise TypeError("Tentative de création d'un RobotCommandSender de "
                            "mauvais type.")
