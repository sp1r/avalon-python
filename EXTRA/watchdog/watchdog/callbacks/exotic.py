# -*- coding: utf-8 -*-
"""
Специфические обработчики событий.
"""
__author__ = 'sp1r'

import subprocess
import os.path

from watchdog.core import Callback


class FakeDBStart(Callback):
    """
    Если необходимая для работы база данных доступна для управления,
    можно автоматически запускать ее.
    """
    # 100% fake
    def __init__(self, event, full_path_to_service):
        Callback.__init__(self, event)
        self.event = event
        self.db = os.path.join(os.path.split(full_path_to_service)[0],
                               'busy.db')

    def run(self):
        print repr(self), repr(self.event)
        subprocess.call('cp %s /tmp/busy.db' % self.db, shell=True)