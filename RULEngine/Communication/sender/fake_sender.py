from RULEngine.Communication.sender.sender_base_class import SenderBaseClass


class FakeSender(SenderBaseClass):

    def connect(self, connection_info):
        return None

    def send_packet(self):
        pass

    def run(self):
        self.logger.info('Fakking')

