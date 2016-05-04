import sys, time
from threading import *

from RULEngine.Strategy.Strategy import Strategy
from RULEngine.Command import Command
from RULEngine.Util.Pose import Pose, Position
from RULEngine.Util.geometry import *
from RULEngine.Util.Pose import Pose, Position
from RULEngine.Util.geometry import *

from UltimateStrat.Executor.CoachExecutor import CoachExecutor
from UltimateStrat.Executor.PlayExecutor import PlayExecutor
from UltimateStrat.Executor.TacticExecutor import TacticExecutor
from UltimateStrat.Executor.SkillExecutor import SkillExecutor
from Util.VectorRegulator import Regulator
import UltimateStrat.Router as Router

from Application import *

__author__ = 'jbecirovski'

class UltimateStrategy(Strategy):
    def __init__(self, field, referee, team, opponent_team, is_team_yellow=False):
        Strategy.__init__(self, field, referee, team, opponent_team)

        # Create InfoManager
        self.team.is_team_yellow = is_team_yellow
        Router.initialize(field, team, opponent_team)
        self.regulator = [Regulator() for x in range(6)]

        # Create Executors
        self.ex_coach = CoachExecutor(Router)
        self.ex_play = PlayExecutor(Router)
        self.ex_tactic = TacticExecutor(Router)
        self.ex_skill = SkillExecutor(Router)

        # Create GUI
        Thread(target=self.create_gui).start()
        self.quit = False

        # Time lock
        self.kicker_time = time.time()
        self.kicker_time_max = 1000

    def create_gui(self):
        gui_mode = True
        if gui_mode:
            root = tk.Tk()
            root
            app = Application(Router, master=root)
            app.mainloop()
            root.destroy()
        self.quit = True

    def on_start(self):
        #if not self.field.ball.position == Position():
        #    self.p_ball = self.field.ball.position
        Router.update()
        # Main Strategy sequence
        self.ex_coach.exec()
        self.ex_play.exec()
        self.ex_tactic.exec()
        self.ex_skill.exec()

        # ::COMMAND SENDER::
        list_autorised_bot = [4]

        for i in list_autorised_bot:
            next_action = Router.getPlayerNextPose(i)
            #if isinstance(next_action, Pose):
                #next_action = self.regulator[i].apply(next_action, debug=True)
            #print(Router.getPlayerPosition(i))
            if isinstance(next_action, Pose):
                # Move Manager :: if next action is Pose
                if Router.getPlayerPose(i) == next_action:
                    #self._send_command(Command.Stop(self.team.players[i], self.team))
                    #self._send_command(Command.MoveToAndRotate(self.team.players[i], self.team, next_action))
                    self._send_command(Command.MoveTo(self.team.players[i], self.team, Router.getPlayerPose(i)))
                    
                else:
                    #self._send_command(Command.MoveToAndRotate(self.team.players[i], self.team, next_action))
                    self._send_command(Command.MoveTo(self.team.players[i], self.team, next_action.position))
            elif isinstance(next_action, int):

                # Kick Manager :: if next action is int
                if not 0 < next_action <= 8:
                    next_action = 5
 
                if get_milliseconds(time.time()) > get_milliseconds(self.kicker_time) + self.kicker_time_max:
                    if get_distance(Router.getPlayerPosition(i), Router.getBallPosition()) < 150:
                        self._send_command(Command.Kick(self.team.players[i], self.team, next_action))
            else:

                # Path Manager :: if next action is list of Pose
                if get_distance(Router.getPlayerPosition(4), next_action[0].position) < 500:
                    #print('NEXT :::::::::::::::::::::::::::::::::::::::::::::::::::')
                    next_pose = next_action.pop(0)
                    if len(next_action) == 0:
                        next_action = next_pose
                    Router.setPlayerNextPose(i, next_action)
                    #self._send_command(Command.MoveToAndRotate(self.team.players[i], self.team, next_pose))
                    self._send_command(Command.MoveTo(self.team.players[i], self.team, next_pose.position))
                else:
                    #self._send_command(Command.MoveToAndRotate(self.team.players[i], self.team, next_action[0]))
                    #print('DISTANCE: ',get_distance(Router.getPlayerPosition(4), next_action[0].position))
                    #print(next_action)
                    self._send_command(Command.MoveTo(self.team.players[i], self.team, next_action[0].position))

        if self.quit:
            exit()


    def on_halt(self):
        self.on_start()

    def on_stop(self):
        self.on_start()
