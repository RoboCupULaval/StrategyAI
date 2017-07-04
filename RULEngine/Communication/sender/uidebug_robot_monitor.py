# Under MIT License, see LICENSE.txt
import threading
from time import sleep, time

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Communication.sender.serial_command_sender import SerialCommandSender
from RULEngine.Command.command import GetBattery
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.constant import PLAYER_PER_TEAM


PERIOD_BETWEEN_BAT_MONITORING = 0.5


class RobotStatus:
    def __init__(self):
        self.battery_lvl = 0
        self.time_since_last_reading = 0


class UIDebugRobotMonitor(object):
    """
        Service pour loguer l'état du robot (niveau batterie, packet lost, etc.) et l'envoyer à l'uidebug
    """
    def __init__(self, serial_com: SerialCommandSender, debug_interface: DebugInterface):
        """ Constructeur """
        self.serial_com = serial_com
        self.debug_interface = debug_interface
        self.robots_status = {}
        for robot_id in range(PLAYER_PER_TEAM):
            self.robots_status[robot_id] = RobotStatus()
        self.terminate = threading.Event()
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.pause_cond = threading.Condition(threading.Lock())

        #self.monitor_thread.start()

    def _monitor_loop(self):
        """ Moniteur le niveau des batteries des robots. """
        return
        while not self.terminate.is_set():
            for robot_id in range(PLAYER_PER_TEAM):
                # Ask for batterie level
                cmd = GetBattery(OurPlayer(None, robot_id), self.pause_cond)
                response = self.serial_com.send_responding_command(cmd)
                if response:
                    # print("Response from id {} with bat lvl {}V".format(robot_id, response))
                    self.robots_status[robot_id].battery_lvl = response
                    self.robots_status[robot_id].time_since_last_reading = time()
                # Send last known state to UI-Debug
                self.debug_interface.send_robot_state(robot_id,
                                                      self.robots_status[robot_id].battery_lvl,
                                                      self.robots_status[robot_id].time_since_last_reading)
                if self.terminate.is_set():
                    return
                sleep(PERIOD_BETWEEN_BAT_MONITORING)

    def stop(self):
        self.terminate.set()
        self.monitor_thread.join()
        self.terminate.clear()
