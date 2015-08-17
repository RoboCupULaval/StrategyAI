import tkinter as tk
import time

from PythonFramework.Framework import start_game
from UltimateStrat.STP.Play.PlayBase import PlayBase
import UltimateStrat.Router as Router


__author__ = 'jbecirovski'

def test(name):
    print('test', name)

class Application(tk.Frame):
    """ Simple GUI for controlling bots on the field. """

    def create_widgets(self):
        # Create and load list of plays
        # self.play_list = tk.Listbox(self)
        # [self.play_list.insert(i, play) for i, play in enumerate(PlayBase().getBook().keys())]
        # self.play_list.pack(side=tk.LEFT)

        # Create control buttons
        tk.Label(self, textvariable=self.current_play).pack(side=tk.TOP, padx=10, pady=10)
        tk.Canvas(self, width=150, height=1, bg="black").pack(padx=10, pady=10)
        for play in self.play_dict:
            tk.Button(self, text=play, command=lambda play=play: self.cb_set_play(play)).pack(side=tk.TOP)
        tk.Canvas(self, width=150, height=1, bg="black").pack(padx=10, pady=10)
        tk.Button(self, text='Quit', command=self.quit).pack(side=tk.TOP)

    def cb_set_play(self, play):
        self.router.setPlay(play)

    def update(self):
        self.current_play.set("PLAY: {}".format(self.router.getCurrentPlay()))
        self.after(100, self.update)

    def __init__(self, router, master=None):
        self.router = router
        self.play_dict = PlayBase().getBook().keys()
        self.current_play = tk.StringVar()
        tk.Frame.__init__(self, master)
        self.pack()
        self.create_widgets()
        self.after(10, self.update)