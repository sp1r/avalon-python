__author__ = 'spir'

import time

import core

start = time.time()

secret = core.b64hash('toor')
print 'Secret hash is:', secret

# initiate ripper
ivan = core.IvanTheRipper(max_length=4)

# add some 'interesting' hash
ivan.add_b64hash(secret)

# run it
ivan()

# get results
print "Elapsed time:", time.time() - start