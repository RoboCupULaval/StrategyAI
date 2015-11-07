import sys
from PythonFramework.Strategy.Strategy import Strategy
from PythonFramework.Command import Command
from UltimateStrat.Executor.CoachExecutor import CoachExecutor
from UltimateStrat.Executor.PlayExecutor import PlayExecutor
from UltimateStrat.Executor.TacticExecutor import TacticExecutor
from UltimateStrat.Executor.SkillExecutor import SkillExecutor
import UltimateStrat.Router as Router
from threading import *
from Application import *
from PythonFramework.Util.Pose import Pose, Position
import sys, time

__author__ = 'jbecirovski'

class UltimateStrategy(Strategy):
    def __init__(self, field, referee, team, opponent_team, is_team_yellow=True):
        Strategy.__init__(self, field, referee, team, opponent_team)

        # Create InfoManager
        self.team.is_team_yellow = is_team_yellow
        Router.initialize(field, team, opponent_team)

        # Create Executors
        self.ex_coach = CoachExecutor(Router)
        self.ex_play = PlayExecutor(Router)
        self.ex_tactic = TacticExecutor(Router)
        self.ex_skill = SkillExecutor(Router)
        #self.p_ball = self.field.ball.position
        # Create GUI
        Thread(target=self.create_gui).start()
        self.quit = False

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

        # send command
        # for i in range(6):
        #     self._send_command(Command.MoveToAndRotate(self.team.players[i], self.team, Router.getPlayerNextPose(i)))
        bot_id = 4

        if Router.getPlayerNextPose(bot_id) == Router.getPlayerPose(bot_id):
            command = Command.Stop(self.team.players[bot_id])
        else:
            #if Router.getPlayerNextPose(bot_id).position == Position():
            #    Router.setPlayerNextPose(bot_id, Pose(self.p_ball, 0))
            test = Router.getPlayerPose(bot_id).position
            ball = Router.getBallPosition()
            print('BALL: x:{} y:{}'.format(ball.x, ball.y))
            print('ROBOT: x:{} y:{}'.format(test.x, test.y))
            temp = Router.getPlayerNextPose(bot_id).position
            command = Command.MoveTo(self.team.players[bot_id], Position(temp.x, temp.y))

        self._send_command(command)

        if self.quit:
            exit()


    def on_halt(self):
        self.on_start()

    def on_stop(self):
        self.on_start()
