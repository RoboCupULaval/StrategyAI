import sys
import logging
from multiprocessing import Process, Queue, Event
from time import sleep


from RULEngine.Communication.receiver.vision_receiver import VisionReceiver
from RULEngine.Communication.sender.uidebug_command_sender import UIDebugCommandSender
from RULEngine.Communication.util.robot_command_sender_factory import RobotCommandSenderFactory
from RULEngine.Controller import Controller
from RULEngine.tracker import Tracker
from config.config_service import ConfigService


class Engine(Process):
    VISION_QUEUE_MAXSIZE = 20
    ROBOT_COMMAND_SENDER_QUEUE_MAXSIZE = 24
    UI_DEBUG_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_RECEIVER_QUEUE_MAXSIZE = 100
    REFEREE_QUEUE_MAXSIZE = 100

    def __init__(self, game_state_queue: Queue, ai_queue: Queue, ui_queue: Queue, stop_event: Event):
        super(Engine, self).__init__(name=__name__)

        self.logger = logging.getLogger("Engine")
        self.cfg = ConfigService()

        self.stop_event = stop_event

        self.vision_queue = Queue(self.VISION_QUEUE_MAXSIZE)
        self.ui_queue = ui_queue
        self.ai_queue = ai_queue
        self.game_state_queue = game_state_queue

        self.tracker = None
        self.controller = None

        self.vision_receiver = None
        self.robot_cmds_sender = None
        self.uidebug_sender = None

    def _initialize_subprocess(self):
        vision_host = self.cfg.config_dict["COMMUNICATION"]["vision_udp_address"]
        vision_port = int(self.cfg.config_dict["COMMUNICATION"]["vision_port"])

        # todo
        uidebug_host = "127.0.0.1"   # self.cfg.config_dict["COMMUNICATION"][""]
        uidebug_port = 15555

        self.vision_receiver = VisionReceiver(vision_host, vision_port, self.vision_queue, self.stop_event)
        self.vision_receiver.daemon = True

        self.uidebug_sender = UIDebugCommandSender(uidebug_host, uidebug_port, self.uidebug_queue, self.stop_event)

        # self.robot_cmds_sender, args = RobotCommandSenderFactory.get_sender()
        # self.robot_cmds_sender(args)

        self.tracker = Tracker(self.vision_queue)
        self.controller = Controller(self.player_cmds_queue)

        self.vision_receiver.start()
        self.uidebug_sender.start()

        self.logger.debug("has initialized.")

    def loop(self):
        while not self.stop_event.is_set():
            self.tracker.execute()
            track_frame = self.tracker.track_frame
            self.game_state_queue.put(track_frame)
            sleep(0)

    def run(self):
        self._initialize_subprocess()
        try:
            self.loop()
        except KeyboardInterrupt:
            pass
        sys.stdout.flush()
        self.stop()
        exit(0)

    def stop(self):
        self.vision_receiver.join(0.3)  # timeout needed for some reason even though the process exit gracefully
        self.logger.debug("VisionReceiver joined now is -> {0}".
                          format("alive" if self.vision_receiver.is_alive() else "dead"))
        self.uidebug_sender.join(0.3)
        logging.debug("UIDebugSender joined now is -> {0}".
                      format("alive" if self.uidebug_sender.is_alive() else "dead"))
