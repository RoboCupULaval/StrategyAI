import logging
from multiprocessing import Process, Queue, Event
from time import sleep

from RULEngine.Communication.vision_communication_manager import VisionCommunicationManager
from RULEngine.Communication.debug_cmds_receiver_communication_manager import DebugCommandReceiverCommunicationManager
from RULEngine.Communication.debug_cmds_sender_communication_manager import DebugCommandSenderCommunicationManager
from RULEngine.Communication.referee_communication_manager import RefereeCommunicationManager
from RULEngine.Communication.robot_cmds_sender_communication_manager import RobotCommandSenderCommunicationManager


class CommunicationManager(Process):
    VISION_QUEUE_MAXSIZE = 100
    ROBOT_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_RECEIVER_QUEUE_MAXSIZE = 100
    REFEREE_QUEUE_MAXSIZE = 100

    def __init__(self, stop_event: Event):
        super(CommunicationManager, self).__init__(name=__name__)

        self.logger = logging.getLogger(__name__)

        self.stop_event = stop_event

        self.vision_queue = Queue(self.VISION_QUEUE_MAXSIZE)
        self.vision_communication_manager = None
        self.logger.debug("Communication Manager initialized")

    def initialize_subprocess(self):
        self.vision_communication_manager = VisionCommunicationManager(self.vision_queue, self.stop_event)
        self.vision_communication_manager.start()

    def orchestrate_communication(self):
        while not self.stop_event.is_set():
            pass

        self.stop()

    def run(self):
        self.initialize_subprocess()
        try:
            self.orchestrate_communication()
        except KeyboardInterrupt:
            pass

    def stop(self):
        self.vision_communication_manager.join()
        logging.debug("Vision Communication Manager joined")
        # self.referee_communication_manager.join()
        # logging.debug("Referee Communication Manager joined")
        # self.robot_command_sender.join()
        # logging.debug("Robot Commands Sender Communication Manager joined")
        # self.ui_debug_command_sender.join()
        # logging.debug("UI-Debug Commands Sender Communication Manager joined")
        # self.ui_debug_command_receiver.join()
        # logging.debug("UI-Debug Receiver Communication Manager joined")
