# -*- coding: utf-8 -*-
"""
Классы-парсеры логов.
"""
__author__ = 'sp1r'

import time

from watchdog.core import Sensor, Event

import Queue


class LogMessage(Event): pass


class LogPickUp(Sensor):
    """
    Генерирует события, при обнаружении в указанном файле
    лога событий уровня WARN и выше.
    """
    def __init__(self, log_file_path):
        Sensor.__init__(self)
        self.check_period = 1

        self.log = None
        while not self.log:
            try:
                self.log = open(log_file_path, 'r')
                self.log.read()  # go to the end
            except IOError:
                pass

        self.log_events = Queue.Queue()

        self.name = 'log_pick_up'

    def check_event(self):
        if self.log_events.empty():
            for line in self.log.readlines():
                level = line.split(':')[0]
                if level in ['WARNING', 'ERROR', 'CRITICAL']:
                    self.log_events.put(LogMessage(self.priority,
                                                   self.name,
                                                   line.strip()))

            # если новых событий не получено - спать
            if self.log_events.empty():
                time.sleep(60)
        else:
            return self.log_events.get()

        return None