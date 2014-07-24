# -*- coding: utf-8 -*-
"""
Механизм работы и базовые классы.
"""
__author__ = 'sp1r'

import thread
import threading
import time
import Queue


class Event:
    """Базовое событие"""
    def __init__(self, priority, source, message):
        self.priority = priority
        self.time = time.time()
        self.source = source
        self.message = message

    def __cmp__(self, other):
        return self.priority < other.priority

    def __repr__(self):
        return ("<%(class_name)s: priority=%(event_priority)d, "
                "source=%(event_source)s, "
                "time=%(event_time)d, "
                "message=\"%(event_message)s\">"
                ) % (dict(
                     class_name=self.__class__.__name__,
                     event_priority=self.priority,
                     event_source=self.source,
                     event_time=int(self.time),
                     event_message=self.message))


class Sensor(threading.Thread):
    """Базовый класс сенсора (генератора событий)."""
    def __init__(self):
        threading.Thread.__init__(self)
        self.priority = 999
        self.event_queue = None
        self.lock = None
        self.check_period = 60  # seconds (default)
        self.name = ""

    def set_priority(self, value):
        self.priority = value

    def configure_communications(self, event_queue, event_queue_lock):
        assert isinstance(event_queue, Queue.PriorityQueue)
        assert isinstance(event_queue_lock, thread.LockType)
        self.event_queue = event_queue
        self.lock = event_queue_lock

    def run(self):
        assert self.event_queue is not None
        assert self.lock is not None
        while True:
            time.sleep(self.check_period)
            event = self.check_event()
            if event is not None:
                with self.lock:
                    self.event_queue.put(event)

    def check_event(self):
        """
        Проверка произошло ли событие.
        Должна возвращать объект Event, если событие произошло. Иначе - None.
        """
        raise NotImplementedError


class Callback(threading.Thread):
    """Базовый класс обработчика событий."""
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.event = event

    def __repr__(self):
        return "<%(class_name)s: event=%(event_class_name)s>" % (dict(
            class_name=self.__class__.__name__,
            event_class_name=self.event.__class__.__name__))


class Reactor:
    """Базовый менеджер."""
    def __init__(self):
        self.event_queue = Queue.PriorityQueue()
        self.lock = threading.Lock()
        self.rules = {}
        self.sensors = []

    def deploy_sensor(self, sensor,
                      callback_class, *callback_args, **callback_kwargs):
        assert isinstance(sensor, Sensor)
        sensor.configure_communications(self.event_queue, self.lock)
        self.rules[sensor.name] = (callback_class,
                                   callback_args,
                                   callback_kwargs)
        sensor.setDaemon(True)
        self.sensors.append(sensor)

    def start(self):
        for sensor in self.sensors:
            sensor.start()
        while True:
            self.process_event(self.event_queue.get())

    def process_event(self, event):
        handler_class, args, kwargs = self.rules[event.source]
        handler = handler_class(event, *args, **kwargs)
        handler.setDaemon(True)
        handler.start()