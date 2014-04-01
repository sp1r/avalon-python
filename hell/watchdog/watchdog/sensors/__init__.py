# -*- coding: utf-8 -*-
"""
Пакет генераторов событий.
"""
__author__ = 'sp1r'

from watchdog.core import Sensor, Event

from phealth import (
    ProcessAliveCheck,
    VMemorySizeCheck,
    CpuPercentCheck,
)

from resources import FakeDBAvailableCheck

from log import LogPickUp


class Phony(Sensor):
    """
    Генерирует сообщение каждую минуту.
    """
    def __init__(self):
        Sensor.__init__(self)
        self.name = 'phony'

    def check_event(self):
        return Event(self.priority, self.name, 'blah-blah-blah')