# -*- coding: utf-8 -*-
"""
Генераторы событий, работающие с /proc/pid/*
"""
__author__ = 'sp1r'

import os

from watchdog.core import Sensor, Event


class ProcessNotExists(Event): pass
class HighMemoryUsage(Event): pass
class HighCpuUsage(Event): pass


def all_pids():
    return reversed([int(x) for x in os.listdir('/proc') if x.isdigit()])


def get_pid_by_path(path, hint=None):
    if hint is not None:
        if os.path.exists('/proc/%s' % hint):
            with open('/proc/%s/cmdline' % hint, 'r') as f:
                if path in f.read():
                    return hint

    for pid in all_pids():
        with open('/proc/%s/cmdline' % pid, 'r') as f:
            if path in f.read():
                return pid

    return None


class ProcessStat:
    def __init__(self, stat_file_contents):
        """
        См. man 5 proc
        """
        self.pid, self.comm, self.state, self.ppid, self.pgrp, self.session, \
            self.tty_nr, self.tpgid, self.flags, self.minflt, self.cminflt, \
            self.majflt, self.cmajflt, self.utime, self.stime, self.cutime, \
            self.cstime, self.priority, self.nice, self.num_threads, \
            self.itrealvalue, self.starttime, self.vsize, self.rss, \
            self.rsslim, self.startcode, self.endcode, self.startstack, \
            self.kstkesp, self.kstkeip, self.signal, self.blocked, \
            self.sigignore, self.sigcatch, self.wchan, self.nswap, \
            self.cnswap, self.exit_signal, self.processor, self.rt_priority, \
            self.policy, self.delayacct_blkio_ticks, self.guest_time, \
            self.cguest_time = stat_file_contents.split(" ")


class ProcessAliveCheck(Sensor):
    """
    Проверяет запущена ли программа full_path_to_program.
    """
    def __init__(self, full_path_to_program):
        Sensor.__init__(self)
        self.pattern = full_path_to_program

        self.name = 'alive_check_by_process_full_path'
        self.target_pid = None

    def check_event(self):
        self.target_pid = get_pid_by_path(self.pattern, hint=self.target_pid)

        if self.target_pid is None:
            return ProcessNotExists(self.priority,
                                    self.name,
                                    'Target process is missing!')


class VMemorySizeCheck(Sensor):
    """
    Проверяет не превышает ли объем памяти процесса full_path_to_program
    заданного порога.
    """
    def __init__(self, full_path_to_program, vsize_threshold):
        Sensor.__init__(self)
        self.pattern = full_path_to_program
        self.threshold = vsize_threshold  # assuming Kbs here

        self.name = 'vsize_check_by_process_full_path'
        self.target_pid = None

    def check_event(self):
        self.target_pid = get_pid_by_path(self.pattern, hint=self.target_pid)

        if self.target_pid is not None:
            with open('/proc/%s/stat' % self.target_pid, 'r') as f:
                stats = ProcessStat(f.read())
            if int(stats.vsize) / 1024 > self.threshold:
                return HighMemoryUsage(self.priority,
                                       self.name,
                                       'Memory usage is very high!')


class CpuPercentCheck(Sensor):
    """
    Проверяет процент потребления процессорного времени процессом
    full_path_to_program.
    """
    def __init__(self, full_path_to_program, cpu_threshold):
        Sensor.__init__(self)
        self.pattern = full_path_to_program
        self.threshold = cpu_threshold

        self.name = 'cpu_percent_check_by_cmd_string'
        self.target_pid = None
        self.check_period = 3

        self.last_total_cpu = 0
        self.last_proc_cpu = 0

    def check_event(self):
        self.target_pid = get_pid_by_path(self.pattern, hint=self.target_pid)

        if self.target_pid is not None:
            with open('/proc/%s/stat' % self.target_pid, 'r') as f:
                stats = ProcessStat(f.read())
            self_usage = int(stats.utime) + int(stats.stime)
            self_delta = self_usage - self.last_proc_cpu
            with open('/proc/stat', 'r') as f:
                for line in f:
                    if line.startswith('cpu '):
                        total_usage = sum(map(lambda x: int(x), line.strip().split()[1:]))
                        break
            total_delta = total_usage - self.last_total_cpu
            percents = 100.0 * self_delta / total_delta
            self.last_proc_cpu = self_usage
            self.last_total_cpu = total_usage
            if percents > self.threshold:
                return HighCpuUsage(self.priority,
                                    self.name,
                                    'Сpu usage is very high!')