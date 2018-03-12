import matplotlib.pyplot as plt


class DynamicUpdate:
    # Suppose we know the x range
    
    def __init__(self):
        self.figure = None
        self.lines = None
        self.ax = None
    
    def on_launch(self):
        # Set up plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([], [], 'o')
        # Auto scale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        # Other stuff
        self.ax.grid()        

    def on_running(self, xdata, ydata):
        # xdata et ydata sont un buffer

        # Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        # Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
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
