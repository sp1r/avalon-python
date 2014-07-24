# -*- coding: utf-8 -*-
"""
Генераторы событий, проверяющие доступность необходимых
сервису внешних ресурсов.
"""
__author__ = 'sp1r'

import os
import sqlite3

from watchdog.core import Sensor, Event


class DBNotAvailable(Event): pass


class FakeDBAvailableCheck(Sensor):
    """
    Подделка. Вместо проверки статуса процесса (например) mysqld,
    проверяет присутствует ли файл sqlite3.
    """
    def __init__(self, sqlite_path):
        Sensor.__init__(self)
        self.db = sqlite_path

        self.name = 'db_availability_check'

    def check_event(self):
        if os.path.exists(self.db) and os.path.isfile(self.db):
            try:
                c = sqlite3.connect(self.db)
                c.close()
                return None
            except sqlite3.OperationalError:
                pass

        return DBNotAvailable(self.priority,
                              self.name,
                              'Required DB is missing!')