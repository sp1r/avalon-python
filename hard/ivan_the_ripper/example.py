__author__ = 'spir'

import time
import os

import core

start = time.time()

# initiate ripper
ivan = core.IvanTheRipper(max_length=5)

# load hashes from file
ivan.add_b64hashes_from_file('hashes.txt')

# run it
ivan()

# get results
print "Elapsed time:", time.time() - start