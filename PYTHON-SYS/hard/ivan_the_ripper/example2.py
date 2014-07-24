# -*- coding: utf-8 -*-
__author__ = 'spir'

import time

import ivanlib

start = time.time()

secret = ivanlib.b64hash('toor')
print 'Secret hash is:', secret

# Инициализируем и настраиваем класс-взломщик
ivan = ivanlib.IvanTheRipper(max_length=3)

# добавляем интересующий нас хэш
ivan.add_b64hash(secret)

# запускаем
ivan()

print "Elapsed time:", time.time() - start