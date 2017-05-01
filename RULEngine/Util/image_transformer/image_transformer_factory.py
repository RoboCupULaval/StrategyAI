from RULEngine.Util.image_transformer.singular_packet_image_transformer import SingularPacketImageTransformer
from RULEngine.Util.image_transformer.kalman_image_transformer import KalmanImageTransformer
from config.config_service import ConfigService


class ImageTransformerFactory(object):

    @staticmethod
    def get_image_transformer():
        type_of_image_transformer = ConfigService().config_dict["IMAGE"]["kalman"]
        if type_of_image_transformer == "true":
            return KalmanImageTransformer()
        elif type_of_image_transformer == "false":
            return SingularPacketImageTransformer()
        else:
            raise TypeError("Tentative de création d'un RobotCommandSender de "
                            "mauvais type.")
