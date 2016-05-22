Under MIT License, see LICENSE.txt
#!/usr/bin/python
from abc import ABCMeta, abstractmethod


class CommandSender(metaclass=ABCMeta):

    @abstractmethod
    def send_command(command):
        pass
