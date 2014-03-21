# -*- coding: utf-8 -*-
"""
Приложение для вскрытия md5 хэшей.

Функциональные возможности:

   1. Получение хэшей в кодировке base64.
   2. Определение кол-ва процессоров на вычислительной системе и параллельный
      запуск соответствующего кол-ва процессов перебора хэшей.
   3. Определение процессорного времени, затраченного на подбор хэша.
"""

__author__ = 'sp1r'

import os
import sys
import string
import base64
import hashlib
import itertools

################################################################################
# Config

input_file_name = "hashes.txt"  # one line - one base64 encoded hash
max_guess_length = 5


################################################################################
# Help Functions

def brute_force(length):
    for combination in itertools.product(string.printable, repeat=length):
        yield ''.join(combination)


def b64hash(pattern):
    return base64.b64encode(hashlib.md5(pattern).digest())


class IvanTheReaper:
    def __init__(self, length, hashes, output):
        self.length = length
        self.hashes_to_break = hashes
        self.output = output

    def __call__(self):
        while self.length <= int(os.environ['MAX']):
            self.break_current_length()
            self.length += int(os.environ['PERIOD'])

    def break_current_length(self):
        for probe in brute_force(self.length):
            probe_hash = b64hash(probe)
            if probe_hash in self.hashes_to_break:
                self.output.write("%s is for: \"%s\"\n" % (probe_hash, probe))
                self.hashes_to_break.remove(probe_hash)

################################################################################
# Logic

if __name__ == "__main__":
    # for i in brute_force(3):
    #     print i

    with open(input_file_name, 'r') as input_file:
        hashes = [line.strip() for line in input_file]

    print "%d hashes was read." % len(hashes)

    os.mkdir(".temp")

    # get number of processors
    cores = os.sysconf("SC_NPROCESSORS_ONLN")

    os.environ['PERIOD'] = str(cores)
    os.environ['MAX'] = str(max_guess_length)

    # start a new proc for every core
    children = {}
    for subproc in range(cores):
        children[subproc] = {'file': os.path.join(os.getcwd(),
                                                  '.temp',
                                                  str(subproc))}
        children[subproc]['pid'] = os.fork()
        if children[subproc]['pid'] == 0:
            with open(children[subproc]['file'], 'w') as out_file:
                reaper = IvanTheReaper(1+subproc, hashes, out_file)
                reaper()
            sys.exit(0)

    for child in children.keys():
        os.waitpid(children[child]['pid'], 0)
        with open(children[child]['file'], 'r') as result_file:
            print result_file.read()
        os.remove(children[child]['file'])

    os.rmdir(".temp")