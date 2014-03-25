__author__ = 'spir'

import time

import ivanlib

start = time.time()

secret = ivanlib.b64hash('toor')
print 'Secret hash is:', secret

# initiate ripper
ivan = ivanlib.IvanTheRipper(max_length=3)

# add some 'interesting' hash
ivan.add_b64hash(secret)

# run it
ivan()

# get results
print "Elapsed time:", time.time() - start