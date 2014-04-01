# -*- coding: utf-8 -*-
"""
Простейшие обработчики событий.
"""
__author__ = 'sp1r'

from watchdog.core import Callback
from watchdog.core.utils import double_fork_start


class StartService(Callback):
    """
    Запуск сервиса.
    """
    def __init__(self, event, full_path_to_service):
        Callback.__init__(self, event)
        self.event = event
        self.path = full_path_to_service

    def run(self):
        print repr(self), repr(self.event)
        double_fork_start(self.path, 'service.py')


class SendMail(Callback):
    """
    Что может быть проще, чем просто известить нас о сбое письмом.
    """
    def __init__(self, event, mail_to):
        Callback.__init__(self, event)
        self.event = event
        self.address = mail_to

    def run(self):
        # Но мы не будем сейчас отправлять сообщения.
        #subprocess.call('echo "%s" | mail -s "Watchdog message" %s' %
        #                (self.event.message, self.address),
        #                shell=True)
        print repr(self), repr(self.event)