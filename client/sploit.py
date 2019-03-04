#!/usr/bin/env python3


import random
import sys
from time import sleep

print(sys.argv[1])

sleep(1)
print("%031d=" % random.randrange(0, 10000), flush=True)

