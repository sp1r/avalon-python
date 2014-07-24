# -*- coding: utf-8 -*-
"""
Пакет обработчиков событий.
"""
__author__ = 'spir'

from watchdog.core import Callback

from simple import (
    StartService,
    SendMail,
)

from exotic import FakeDBStart


class Echo(Callback):
    """
    Выводит полученное событие.
    """
    def __init__(self, event):
        Callback.__init__(self, event)

    def run(self):
        print repr(self), repr(self.event)