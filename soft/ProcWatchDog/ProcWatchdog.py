#!/usr/bin/python
# -*- coding: utf-8 -*- 
# usage: ./ProcWatchdog.py <configfile>

import sys
import ConfigParser 
import syslog
import subprocess


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
		pop = subprocess.Popen(self.cmd, shell=True, cwd=self.cwd, env=self.envs, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		self.stdout, self.stderr = pop.communicate()	
		return 1 if pop.wait() else 0
		
	def watch(self, count):
		"""
		Запуск процесса и наблюдение за его состоянием.
		args: count - количество перезапусков процесса в случае нештатного завершения.
		"""
		syslog.syslog('Starting WatchDog: `%s`' % self.cmd)		
		c = 0
		while self.run() and c < count:
			syslog.syslog(syslog.LOG_ERR, 'Service `%s` restarted.\nCrash reason:\n %s' % (self.cmd, self.stderr))
			c+=1	 	
		syslog.syslog('Stopping WatchDog')	
	
s = watchdog(sys.argv[1])
s.watch(100)
print s.stdout


