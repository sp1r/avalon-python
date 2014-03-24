# -*- coding: utf-8 -*-


__author__ = 'sp1r'

import os
import sys
import string
import base64
import hashlib
import itertools
import time


class IvanTheRipper:
    """
    Класс для вскрытия md5 хэшей.

    Функциональные возможности:
       1. Получение хэшей в кодировке base64.
       2. Определение кол-ва процессоров на вычислительной системе и
          параллельный запуск соответствующего кол-ва процессов перебора хэшей.
       3. Определение процессорного времени, затраченного на подбор хэша.
    """
    def __init__(self, max_length=3):
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
        """
        print 'Start Ripping! Got', len(self.hashes), 'hashes to break.'
        total_cores = get_processors_num()
        subprocs = []
        for core in range(total_cores):
            pid = os.fork()
            if not pid:
                w = Worker(self.max_length, core + 1, total_cores, self.hashes)
                w()
                sys.exit()
            else:
                subprocs.append(pid)

        for proc in subprocs:
            os.waitpid(proc, 0)


class Worker:
    def __init__(self, max_length, worker_number, total_workers, hashes):
        """
        Каждый Worker будет перебирать только часть строк пропорциональную
        worker_number/total_worker.
        """
        self.first_char = \
            len(string.printable)*(worker_number - 1)/total_workers

        if worker_number == total_workers:
            self.last_char = len(string.printable) - 1
        else:
            self.last_char = \
                len(string.printable)*worker_number/total_workers
        self.max = max_length
        self.hashes_to_break = hashes

    def __call__(self):
        for probe_length in range(self.max):
            self.rip(probe_length + 1)

    def rip(self, length):
        for probe in self.partial_brute_force(length):
            probe_hash = b64hash(probe)
            if probe_hash in self.hashes_to_break:
                #self.output.write("%s is for: \"%s\"\n" % (probe_hash, probe))
                print "%s is for: \"%s\" (cpu time: %f)\n" % (probe_hash,
                                                              probe,
                                                              time.clock())
                self.hashes_to_break.remove(probe_hash)

    def partial_brute_force(self, length):
        if length == 1:
            for char in string.printable[self.first_char:self.last_char]:
                yield char
        else:
            for char in string.printable[self.first_char:self.last_char]:
                for combination in itertools.product(string.printable,
                                                     repeat=(length - 1)):
                    yield char + ''.join(combination)


################################################################################
# Help Functions

def get_processors_num():
    return os.sysconf("SC_NPROCESSORS_ONLN")


def brute_force(length):
    for combination in itertools.product(string.printable, repeat=length):
        yield ''.join(combination)


def b64hash(pattern):
    return base64.b64encode(hashlib.md5(pattern).digest())