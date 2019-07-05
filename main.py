#!/usr/bin/env python
import sys
import os
import logging
from src.controller import Controller

if len(sys.argv) == 1:
    print("usage {} desktop|hat".format(os.path.basename(sys.argv[0])))
    sys.exit(1)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

Controller(sys.argv[1] == "hat").start()
