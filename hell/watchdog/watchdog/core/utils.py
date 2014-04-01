# -*- coding: utf-8 -*-
"""
Shortcuts.
"""
__author__ = 'sp1r'

import os
import sys


def double_fork_start(path, *args):
    pid = os.fork()
    if pid == 0:
        second_pid = os.fork()
        if second_pid == 0:
            os.execl(path, *args)
        else:
            sys.exit(0)