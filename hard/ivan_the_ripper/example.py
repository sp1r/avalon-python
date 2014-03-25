# -*- coding: utf-8 -*-
__author__ = 'spirit'

import time

import ivanlib

start = time.time()

# Инициализируем и настраиваем класс-взломщик
ivan = ivanlib.IvanTheRipper(max_length=4)

# загружаем список хэшей из файла
ivan.add_b64hashes_from_file('hashes.txt')

# запускаем
ivan()

print "Elapsed time:", time.time() - start
