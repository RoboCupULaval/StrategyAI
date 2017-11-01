from multiprocessing import Queue, Event
import logging

from multiprocessing import Process

from RULEngine.Communication.vision_communication_manager import VisionCommunicationManager
from RULEngine.Communication.debug_cmds_receiver_communication_manager import DebugCommandReceiverCommunicationManager
from RULEngine.Communication.debug_cmds_sender_communication_manager import DebugCommandSenderCommunicationManager
from RULEngine.Communication.referee_communication_manager import RefereeCommunicationManager
from RULEngine.Communication.robot_cmds_sender_communication_manager import RobotCommandSenderCommunicationManager


class CommunicationManager():
    VISION_QUEUE_MAXSIZE = 100
    ROBOT_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_RECEIVER_QUEUE_MAXSIZE = 100
    REFEREE_QUEUE_MAXSIZE = 100

    def __init__(self):
        self.stop_event = Event()
        self.vision_queue = None
        self.vision_communication_manager = None

    def initialize(self):
        logging.debug("Communication Manager initializing")

        self.vision_queue = Queue(self.VISION_QUEUE_MAXSIZE)
        self.vision_communication_manager = Process(target=VisionCommunicationManager, args=(self.vision_queue,
                                                                                             self.stop_event),
                                                    name="RobocupULaval - Vision Comm Manager")
        self.vision_communication_manager.start()
        print(self.vision_communication_manager)

        # self.robot_command_sender_queue = Queue(self.ROBOT_COMMAND_SENDER_QUEUE_MAXSIZE)
        # self.robot_command_sender = RobotCommandSenderCommunicationManager(self.robot_command_sender_queue,
        #                                                                    self.stop_event)
        #
        # self.ui_debug_command_sender_queue = Queue(self.UI_DEBUG_COMMAND_SENDER_QUEUE_MAXSIZE)
        # self.ui_debug_command_sender = DebugCommandSenderCommunicationManager(self.ui_debug_command_sender_queue,
        #                                                                       self.stop_event)
        #
        # self.ui_debug_command_receiver_queue = Queue(self.UI_DEBUG_COMMAND_RECEIVER_QUEUE_MAXSIZE)
        # self.ui_debug_command_receiver = DebugCommandReceiverCommunicationManager(self.ui_debug_command_receiver_queu
        #                                                                           self.stop_event)
        #
        # self.referee_queue = Queue(self.REFEREE_QUEUE_MAXSIZE)
        # self.referee_communication_manager = RefereeCommunicationManager(self.referee_queue,
        #                                                                  self.stop_event)
        logging.debug("Communication Manager initialized")

    def stop(self):
        self.stop_event.set()
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
