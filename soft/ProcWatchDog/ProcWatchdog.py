#!/usr/bin/python
# -*- coding: utf-8 -*- 
# version 0.1
# usage: ./ProcWatchdog.py <configfile>


# Не судите строго, первая попытка.
# Вопросы:
# 1. Формат приведенный в задании - не ini формат, это было сделано специально дабы не использовать модули типа ConfigParser?
# 2. Какие пользовательские комманды программа должна уметь исполнять?

# Нерешенные проблемы:
# 1. Бесконечная рекурсия при неверно данной команде.
# 2. Вывод stdout дочернего процесса.
# 3. Обработка разных исключений с пояснением в логе.


import sys
import os
import ConfigParser 
import datetime
import syslog


def runcmd(ini):
	syslog.syslog('reading configuration...')	
	config = ConfigParser.ConfigParser()
	config.read(ini)

	os.chdir(config.get('process name', 'workdir'))
	cmdline = config.get('process name', 'cmdline')
	file = cmdline.split(' ')[0]
	args = cmdline.split(' ')
	childpid = os.fork()
	if childpid:
		result = os.waitpid(childpid, 0)	
		if result[1] == 0:
			syslog.syslog(syslog.LOG_NOTICE, 'normal exit (pid:%d, code:%d)' % result)
		else:
			syslog.syslog(syslog.LOG_ERR,'exit with error (pid:%d, code:%d)' % result)
			runcmd(sys.argv[1])
		
	else:
		syslog.syslog(syslog.LOG_NOTICE, 'starting: `%s` with PID %d...' % (cmdline, os.getpid()))
		os.environ = {'var1': config.get('environment', 'var1'), 'var2': config.get('environment', 'var2')}
		os.execvpe(file, args, os.environ)
syslog.syslog('Starting WatchDog')

try:
	runcmd(sys.argv[1])
except: 
	syslog.syslog(syslog.LOG_CRIT, 'ProcWatchdog crashed')
