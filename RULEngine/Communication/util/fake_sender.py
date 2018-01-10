from RULEngine.Communication.sender.sender_base_class import SenderBaseClass


class FakeSender(SenderBaseClass):

    def __init__(self, *args, **kwargs):
        pass

    def send_packet(self):
        pass

    def run(self):
        pass

