#!/usr/bin/python
# -*- coding: utf-8 -*- 
# usage: ./ProcWatchdog.py <configfile>

import sys
import ConfigParser 
import syslog
import subprocess
import os 


class watchdog:
	"""
	Класс watchdog.

	Функциональные возможности:
	1. Получение параметров из конфигурационного файла.
	2. Установка текущего каталога и переменных окружения для запускаемых процессов.
	3. Запись в системный журнал уведомления о нештатном завершении процесса с указанием причины.
	
	args: ini - файл конфигурации определенного формата:
		[process name]
		command_line = string
		working_dir = string

		[environment]
		var = value
		var = value
		...
	"""
	def __init__(self, ini):	
		self.ini = ini 
		syslog.syslog('reading configuration...')	
		config = ConfigParser.ConfigParser()
                config.read(self.ini)
		self.cmd = config.get('process name', 'cmdline')
		self.cwd = config.get('process name', 'workdir')
		self.envs = {}
		for el in config.items('environment'):
                	self.envs[el[0]]=el[1]

			
	def run(self):
		"""
		Запуск процесса с пользовательской коммандой.
		"""
		pop = subprocess.Popen(self.cmd, shell=True, cwd=self.cwd, env=self.envs)
		self.pid = pop.pid
		self.code = os.wait()[1]
		return self.code if self.code else 0
		
	def watch(self, count):
		"""
		Запуск процесса и наблюдение за его состоянием.
		args: count - количество перезапусков процесса в случае нештатного завершения.
		"""
		syslog.syslog('Starting WatchDog: `%s`' % self.cmd)		
		c = 0

		self.code = 1
		while self.code and c < count:
			self.run()
			
			if not self.code:
				syslog.syslog('Process exit normally')
				break
			elif os.WIFSIGNALED(self.code):
				self.result = 'terminated with signal %d' % os.WTERMSIG(self.code)
			elif os.WIFSTOPPED(self.code):
				self.result = 'stopped with signal %d' % os.WSTOPSIG(self.code)
			else:
				self.result = 'magic error'
			
			syslog.syslog(syslog.LOG_ERR, 'Service `%s` restarted.\nCrash reason: %s\n' % (self.cmd, self.result)) 
			c+=1	 
			
		syslog.syslog('Stopping WatchDog')	
	
s = watchdog(sys.argv[1])
s.watch(100)


