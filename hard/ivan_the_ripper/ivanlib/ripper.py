# -*- coding: utf-8 -*-
"""
TODO:
1. Попробовать сделать общий доступ из субпроцессов к списку хэшей в
   родительском на чтение. В родительском же постепенно удалять из него
   хэши, которые уже подобраны.
"""
__author__ = 'sp1r'

import os
import string
import base64
import hashlib
import itertools
import time
import multiprocessing as mp
import Queue


class IvanTheRipper:
    """
    Класс для вскрытия md5 хэшей.

    Функциональные возможности:
       1. Получение хэшей в кодировке base64.
       2. Определение кол-ва процессоров на вычислительной системе и
          параллельный запуск соответствующего кол-ва процессов перебора хэшей.
       3. Определение процессорного времени, затраченного на подбор хэша.
    """
    def __init__(self, max_length=12):
        self.max_length = max_length
        self.hashes = []

    ############################################################################
    # Управление списком хэшей.

    def add_b64hashes_from_file(self, filename):
        """
        Файл должен содержать хэши по одной штуке в строке.
        Одна строка - один хэш в кодировке base64.

        Если будут другие строки - программа конечно не сломается, но будет
        пробовать подбирать их тоже. Оно вам надо?
        """
        with open(filename, 'r') as f:
            hashes_from_file = [line.strip() for line in f]
        self.hashes.extend(hashes_from_file)

    def add_b64hash(self, hash_string):
        """
        Добавляет один хэш в список поиска.

        Аргументы:
           hash_string -- (str) md5-хэш в кодировке base64.
        """
        self.hashes.append(hash_string)

    def clear_hashes_list(self):
        """
        Удаляет все заргуженные ранее хэши.
        """
        self.hashes = []

    ############################################################################
    # Логика

    def __call__(self):
        """
        Наиболее трудоемкая часть работы - генерация хэшей.
        Ее и будем распараллеливать.
        """
        print 'Start Ripping! Got', len(self.hashes), 'hashes to break.'

        results = mp.Queue()

        total_cores = get_processors_num()
        subprocs = []
        active_children = 0
        for core in range(total_cores):
            child_instance = Worker(core, total_cores, self.hashes, results)
            child_process = mp.Process(target=child_instance,
                                       args=(self.max_length, ))
            child_process.start()
            active_children += 1
            subprocs.append(child_process)

        # Возможно 2 штатных случая завершения работы:
        # a) все подпроцессы завершились
        # б) подобраны все хэши
        while active_children and self.hashes:
            try:
                r = results.get(timeout=5)
                print r
                self.hashes.remove(r[0])
            except Queue.Empty:
                pass

            for child in subprocs:
                child.join(timeout=1)
                if child.exitcode is not None:
                    subprocs.remove(child)
                    active_children -= 1

        # Если еще есть живые подпроцессы - убить их
        if active_children:
            for child in subprocs:
                child.terminate()


class Worker:
    def __init__(self, worker_number, total_workers, hashes, results_queue):
        """
        Каждый Worker будет перебирать только часть строк пропорциональную
        worker_number/total_worker.

        Аргументы:
           worker_number -- (int) порядковый номер процесса в рабочей группе,
                            от 0 до N-1.
           total_workers -- (int) суммарное количество процессов в группе (N).
           hashes -- (list of str) список md5-хэшей в кодировке base64, которые
                     будут подбираться.
        """
        self.first_char = \
            len(string.printable)*worker_number/total_workers

        if worker_number == total_workers:
            self.last_char = len(string.printable) - 1
        else:
            self.last_char = \
                len(string.printable)*(worker_number + 1)/total_workers

        self.hashes_to_break = hashes
        self.results = results_queue

    def __call__(self, max_length):
        for probe_length in range(max_length):
            self.rip(probe_length + 1)

    def rip(self, length):
        for probe in self.partial_brute_force(length):
            probe_hash = b64hash(probe)
            if probe_hash in self.hashes_to_break:
                self.results.put((probe_hash, probe, time.clock()))
                self.hashes_to_break.remove(probe_hash)

    def partial_brute_force(self, length):
        if length == 1:
            for char in string.printable[self.first_char:self.last_char]:
                yield char
        else:
            for char in string.printable[self.first_char:self.last_char]:
                for combination in brute_force(length - 1):
                    yield char + combination


################################################################################
# Help Functions

def get_processors_num():
    return os.sysconf("SC_NPROCESSORS_ONLN")


def brute_force(length):
    for combination in itertools.product(string.printable, repeat=length):
        yield ''.join(combination)


def b64hash(pattern):
    return base64.b64encode(hashlib.md5(pattern).digest())