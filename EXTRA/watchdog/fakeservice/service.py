#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Псевдо-сервис используемый в демонстрации.
"""
__author__ = 'sp1r'

import os
import sys
import logging
import time
import sqlite3

import itertools
import hashlib
import random


class VeryBusyService:
    def __init__(self):
        with open('/tmp/busy.log', 'a') as f:
            f.write('=== Start new session ===\n')
        logging.basicConfig(filename='/tmp/busy.log', level=logging.INFO)
        self.heap = []

    def __call__(self, *args, **kwargs):
        while True:
            # запишем что-нибудь в лог...
            logging.info('Working very hard now...')

            # займемся вычислениями...
            for x in range(8):
                junk = [hashlib.sha512(''.join(f)).hexdigest()
                        for f in itertools.product('qwerty', repeat=x)]

            # сгенерируем какие-нибудь предупреждения
            self.heap.append(junk)
            if len(self.heap) > 10:
                logging.error('Have too much junk!')
            elif len(self.heap) > 5:
                logging.warning('Junk level is high.')

            # подключимся к базе данных...
            if os.path.exists('/tmp/busy.db'):
                try:
                    db = sqlite3.connect('/tmp/busy.db')
                    # query here
                    db.close()
                except sqlite3.OperationalError:
                    logging.error('Database error.')
            else:
                logging.error('No database found.')

            time.sleep(15)

            self.unstable()  # danger!

    def unstable(self):
        if random.randint(0, 20) == 3:
            logging.critical('How can I live after this?!')
            logging.shutdown()
            sys.exit(1)

if __name__ == "__main__":
    os.setpgrp()
    instance = VeryBusyService()
    instance()