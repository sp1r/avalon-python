__author__ = 'spir'

import time
import os

import ivanlib

start = time.time()

# initiate ripper
ivan = ivanlib.IvanTheRipper(max_length=4)

# load hashes from file
ivan.add_b64hashes_from_file('hashes.txt')

# run it
ivan()

# get results
print "Elapsed time:", time.time() - start