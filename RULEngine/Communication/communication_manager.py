from RULEngine.Communication.receiver.referee_receiver import RefereeReceiver
from RULEngine.Communication.util.robot_command_sender_factory import RobotCommandSenderFactory
from multiprocessing import Queue, Event


class CommunicationManager():
    REFEREE_QUEUE_MAXSIZE = 100
    ROBOT_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_RECEIVER_QUEUE_MAXSIZE = 100

    def __init__(self):
        self.stop_event = Event()

        self.referee_queue = Queue(self.REFEREE_QUEUE_MAXSIZE)
        self.referee_receiver = RefereeReceiver(self.referee_queue, self.stop_event)

        self.robot_command_sender = RobotCommandSenderFactory.get_sender()
        self.robot_command_sender_queue = Queue(self.ROBOT_COMMAND_SENDER_QUEUE_MAXSIZE)

        self.ui_debug_command_sender = None
        self.ui_debug_command_sender_queue = Queue(self.UI_DEBUG_COMMAND_SENDER_QUEUE_MAXSIZE)

        self.ui_debug_command_receiver = None
        self.ui_debug_command_receiver_queue = Queue(self.UI_DEBUG_COMMAND_RECEIVER_QUEUE_MAXSIZE)


    def start(self):
        self.referee_receiver.start()
        self.robot_command_sender.start()
        self.ui_debug_command_sender.start()
        self.ui_debug_command_receiver.start()

    def stop(self):
        self.stop_event.set()
        self.referee_receiver.join()
        self.robot_command_sender.join()
        self.ui_debug_command_sender.join()
        self.ui_debug_command_receiver.join()
