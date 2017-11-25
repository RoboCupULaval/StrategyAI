import logging
from multiprocessing import Process, Queue, Event
from time import sleep

from RULEngine.Communication.receiver.vision_receiver import VisionReceiver
from RULEngine.Communication.vision_manager import VisionManager
from RULEngine.Communication.debug_cmds_receiver_communication_manager import DebugCommandReceiverCommunicationManager
from RULEngine.Communication.debug_cmds_sender_communication_manager import DebugCommandSenderCommunicationManager
from RULEngine.Communication.referee_communication_manager import RefereeCommunicationManager
from RULEngine.Communication.robot_cmds_sender_communication_manager import RobotCommandSenderCommunicationManager
from RULEngine.tracker import Tracker
from config.config_service import ConfigService


class Engine(Process):
    VISION_QUEUE_MAXSIZE = 20
    ROBOT_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_RECEIVER_QUEUE_MAXSIZE = 100
    REFEREE_QUEUE_MAXSIZE = 100

    def __init__(self, stop_event: Event):
        super(Engine, self).__init__(name=__name__)

        self.logger = logging.getLogger("Engine")
        self.cfg = ConfigService()

        self.stop_event = stop_event

        self.vision_queue = Queue(self.VISION_QUEUE_MAXSIZE)
        self.ui_debug_sender = None
        self.tracker = Tracker(self.vision_queue)

        self.vision_receiver = None

    def initialize_subprocess(self):
        host = self.cfg.config_dict["COMMUNICATION"]["referee_udp_address"]
        port = int(self.cfg.config_dict["COMMUNICATION"]["referee_port"])

        self.vision_receiver = VisionReceiver(host, port, self.vision_queue, self.stop_event)
        self.vision_receiver.daemon = True
        self.vision_receiver.start()

        self.logger.debug("has initialized.")

    def loop(self):
        while not self.stop_event.is_set():
            print(self.vision_queue.qsize())

    def run(self):
        self.initialize_subprocess()
        try:
            self.loop()
        except KeyboardInterrupt:
            pass
        self.stop()
        exit(0)

    def stop(self):
        self.vision_receiver.join(0.3)  # timeout needed for some reason even though the process exit gracefully
        self.logger.debug("VisionCommunicationManager joined now is -> {0}".
                          format("alive" if self.vision_receiver.is_alive() else "dead"))
        # self.referee_communication_manager.join()
        # logging.debug("Referee Communication Manager joined")
        # self.robot_command_sender.join()
        # logging.debug("Robot Commands Sender Communication Manager joined")
        # self.ui_debug_command_sender.join()
        # logging.debug("UI-Debug Commands Sender Communication Manager joined")
        # self.ui_debug_command_receiver.join()
        # logging.debug("UI-Debug Receiver Communication Manager joined")
