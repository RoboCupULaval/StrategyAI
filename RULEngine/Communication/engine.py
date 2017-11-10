import logging
from multiprocessing import Process, Queue, Event
from time import sleep

from RULEngine.Communication.vision_manager import VisionManager
from RULEngine.Communication.debug_cmds_receiver_communication_manager import DebugCommandReceiverCommunicationManager
from RULEngine.Communication.debug_cmds_sender_communication_manager import DebugCommandSenderCommunicationManager
from RULEngine.Communication.referee_communication_manager import RefereeCommunicationManager
from RULEngine.Communication.robot_cmds_sender_communication_manager import RobotCommandSenderCommunicationManager


class Engine(Process):
    VISION_QUEUE_MAXSIZE = 100
    ROBOT_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_RECEIVER_QUEUE_MAXSIZE = 100
    REFEREE_QUEUE_MAXSIZE = 100

    def __init__(self, stop_event: Event):
        super(Engine, self).__init__(name=__name__)

        self.logger = logging.getLogger("CommunicationManager")

        self.stop_event = stop_event

        self.vision_queue = Queue(self.VISION_QUEUE_MAXSIZE)
        self.vision_communication_manager = None

    def initialize_subprocess(self):
        self.vision_communication_manager = VisionManager(self.vision_queue, self.stop_event)
        self.vision_communication_manager.start()

        self.logger.debug("Engine has initialized.")

    def orchestrate_communication(self):
        while not self.stop_event.is_set():
            sleep(0.01)

    def run(self):
        self.initialize_subprocess()
        try:
            self.orchestrate_communication()
        except KeyboardInterrupt:
            pass
        self.stop()
        exit(0)

    def stop(self):
        self.vision_communication_manager.join()
        self.logger.debug("VisionCommunicationManager joined with {0}".
                          format(self.vision_communication_manager.exitcode))
        # self.referee_communication_manager.join()
        # logging.debug("Referee Communication Manager joined")
        # self.robot_command_sender.join()
        # logging.debug("Robot Commands Sender Communication Manager joined")
        # self.ui_debug_command_sender.join()
        # logging.debug("UI-Debug Commands Sender Communication Manager joined")
        # self.ui_debug_command_receiver.join()
        # logging.debug("UI-Debug Receiver Communication Manager joined")
