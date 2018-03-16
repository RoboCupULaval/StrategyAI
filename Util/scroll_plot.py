import matplotlib.pyplot as plt


class DynamicUpdate:
    # Suppose we know the x range

    def __init__(self):
        self.figure = None
        self.lines = None
        self.axes = None

    def on_launch(self):
        # Set up plot
        self.figure, self.axes = plt.subplots()
        self.lines, = self.axes.plot([], [], 'o')
        # Auto scale on unknown axis and known lims on the other
        self.axes.set_autoscaley_on(True)
        # Other stuff
        self.axes.grid()

    def on_running(self, xdata, ydata):
        # xdata et ydata sont un buffer

        # Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        # Need both of these in order to rescale
        self.axes.relim()
        self.axes.autoscale_view()
        # We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    # Example
    def __call__(self):
        import numpy as np
        import time
        self.on_launch()
        xdata = range(300)
        ydata = np.zeros(300)
        while 1:
            ydata[:-1] = ydata[1:]
            ydata[-1] = np.random.normal()
            self.on_running(xdata, ydata)
            time.sleep(0.01)
