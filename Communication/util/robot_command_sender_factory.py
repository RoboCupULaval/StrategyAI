from RULEngine.Communication.sender.grsim_command_sender \
    import GrSimCommandSender
from RULEngine.Communication.sender.serial_command_sender \
    import SerialCommandSender


class RobotCommandSenderFactory(object):

    @staticmethod
    def get_sender(type_of_connection):
        if type_of_connection == "disabled":
            return GrSimCommandSender("127.0.0.1", 20011)
        elif type_of_connection == "rf" or type_of_connection == "bluetooth":
            return SerialCommandSender(serial_type=type_of_connection)
        else:
            raise TypeError("Tentative de création d'un RobotCommandSender de "
                            "mauvais type.")
