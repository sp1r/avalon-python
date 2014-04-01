#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Демонстрация работы watchdog.

В данной конфигурации отслеживает следующие параметры:
 - сервис выполняется;
 - потребление памяти не выше 100Mb;
 - потребление cpu не выше 20%;
 - лог-файл не содержит сообщений WARN и выше;
 - требуемая база данных доступна.

Установлены следующие правила поведения:
   сервис не обнаружен => запустить сервис
   превышение потребления памяти => e-mail
   превышение потребления процессора => e-mail
   предупреждения/ошибки в логах => e-mail
   недоступна база данных => запуск базы данных (эмуляция)
"""
__author__ = 'sp1r'

import os
import sys
import signal

from watchdog.core import Reactor

from watchdog.sensors import (
    ProcessAliveCheck,
    VMemorySizeCheck,
    CpuPercentCheck,
    FakeDBAvailableCheck,
    LogPickUp,
)

from watchdog.callbacks import (
    StartService,
    SendMail,
    FakeDBStart,
)

from watchdog.core.utils import double_fork_start

if __name__ == "__main__":

    # вычисляем, где находится сервис
    script_exec = sys.argv[0]
    head, tail = os.path.split(script_exec)
    if os.path.isabs(script_exec):
        path_to_service = os.path.join(head,
                                       'fakeservice',
                                       'service.py')
    else:
        path_to_service = os.path.join(os.getcwd(),
                                       head,
                                       'fakeservice',
                                       'service.py')

    # нам безразлична судьба дочерних процессов
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    # запустим сервис
    double_fork_start(path_to_service, 'service.py')

    # Конфигурация
    sensors = {
        'alive': {'sensor_class': ProcessAliveCheck,
                  'sensor_priority': 1,
                  'sensor_args': (path_to_service,),
                  'callback': StartService,
                  'callback_args': (path_to_service,)},

        'mem':   {'sensor_class': VMemorySizeCheck,
                  'sensor_priority': 5,
                  'sensor_args': (path_to_service, 102400),
                  'callback': SendMail,
                  'callback_args': ("me@bestdomain.ever",)},

        'cpu':   {'sensor_class': CpuPercentCheck,
                  'sensor_priority': 5,
                  'sensor_args': (path_to_service, 20.0),
                  'callback': SendMail,
                  'callback_args': ("me@bestdomain.ever",)},

        'db':    {'sensor_class': FakeDBAvailableCheck,
                  'sensor_priority': 10,
                  'sensor_args': ('/tmp/busy.db',),
                  'callback': FakeDBStart,
                  'callback_args': (path_to_service,)},

        'log':   {'sensor_class': LogPickUp,
                  'sensor_priority': 20,
                  'sensor_args': ('/tmp/busy.log',),
                  'callback': SendMail,
                  'callback_args': ("me@bestdomain.ever",)},
    }

    # создаем и запускаем watchdog
    wg = Reactor()

    for label, config in sensors.items():
        sensor = config['sensor_class'](*config['sensor_args'])
        sensor.set_priority(config['sensor_priority'])
        wg.deploy_sensor(sensor, config['callback'], *config['callback_args'])

    wg.start()