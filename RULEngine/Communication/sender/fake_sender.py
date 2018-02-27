from RULEngine.Communication.sender.sender_base_class import Sender


class FakeSender(Sender):

    def connect(self, connection_info):
        return None

    def send_packet(self, packet):
        pass

    def run(self):
        self.logger.info('Fakking')

