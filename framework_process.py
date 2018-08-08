# Under MIT License, see LICENSE.txt
import cProfile
import logging
import os
from abc import ABCMeta, abstractmethod

from multiprocessing import Process

from time import time
from Util.timing import create_fps_timer

from config.config import Config
config = Config()


class FrameworkProcess(Process, metaclass=ABCMeta):

    def __init__(self, framework):

        super().__init__(name=self.name)

        self.config = Config()[self.name.upper()]
        self.framework = framework

        self.logger = logging.getLogger(self.name)
        self.profiler = None

        self.fps = self.config['fps']
        self.is_fps_locked = self.config['is_fps_locked']
        self.dt = 0.0
        self.last_time = 0.0

        self.frame_count = 0
        self.last_frame_count = 0

        def callback(excess_time):
            if excess_time > self.config['max_excess_time']:
                self.logger.debug(f'Overloaded ({int(1000*excess_time)} ms behind schedule)')

        self.fps_sleep = create_fps_timer(self.fps, on_miss_callback=callback)

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def pid(self):
        return os.getpid()

    def wait_until_ready(self):
        pass

    @abstractmethod
    def main_loop(self):
        pass

    def run(self):

        self.logger.debug(self.status())

        self.profiler = cProfile.Profile()
        if self.framework.profiling:
            self.profiler.enable()

        try:

            self.wait_until_ready()

            self.last_time = time()
            while True:
                self.frame_count += 1
                self.update_time()
                self.main_loop()
                if self.is_fps_locked: self.fps_sleep()
                self.framework.watchdogs[self.name].value = time()

        except KeyboardInterrupt:
            self.logger.debug('Interrupted.')
        except BrokenPipeError:
            self.logger.exception('A connection was broken.')
        except:
            self.logger.exception('An error occurred.')
        finally:
            self.stop()

    def status(self) -> str:
        if super().is_alive():
            status_string = f'Running with process ID {self.pid}'
            if self.is_fps_locked:
                status_string += f' at {self.fps} fps.'
            else:
                status_string += ' without fps limitation.'
        else:
            status_string = 'Not running.'

        return status_string

    def update_time(self):
        current_time = time()
        self.dt = current_time - self.last_time
        self.last_time = current_time

    def dump_profiling_stats(self):
        if self.framework.profiling:
            filename = f'profile_data_{self.name}.prof'
            self.profiler.dump_stats(filename)
            self.logger.debug(f'Profiling data written to {filename}.')

    def is_alive(self) -> bool:

        if not __debug__:  # Prevent the process from dying if the process is being debugged
            if time() - self.framework.watchdogs[self.name].value > self.framework.MAX_HANGING_TIME:
                self.logger.critical('Process is hanging. Shutting down.')
                return False

        return super().is_alive()

    def stop(self):
        self.dump_profiling_stats()
        self.logger.debug('Stopped.')
