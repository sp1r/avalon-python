#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Сетевой сервис, выполняющий команды оболочки, переданные по сети клиентами, и возвращающий клиентам стандартный вывод и поток ошибок выполненных команд. В качестве транспорта должен использоваться протокол TCP. Признаком завершения команды является символ новой строки.
Функциональные возможности:

Получение параметров из конфигурационного файла.
(Квази)одновременное обслуживание множества клиентов.
Ограничение максимального времени выполнения команды.
Формат конфигурационного файла:
[config]
address = string
port = num
timeout = num
working_dir = string
"""
import subprocess
import asyncore
import socket
import signal
import ConfigParser

def alarm_handler(signum, frame):
    raise Alarm


class Alarm(Exception):
    pass

class Handler(asyncore.dispatcher_with_send):

	def handle_read(self):
		data = self.recv(8192)
		if data == 'q\r\n': # Выход из сессии.
			self.close()
		if data:
			signal.signal(signal.SIGALRM, alarm_handler)
			signal.alarm(int(config.get('config', 'timeout')))
			try:
				pop = subprocess.Popen(data.strip(), shell=True, cwd=config.get('config', 'working_dir'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				stdin, stderr = pop.communicate()
				signal.alarm(0)
				self.send(stdin + stderr)
			except Alarm:
				self.send('command takes more than %s second(s)\n' % config.get('config', 'timeout'))
					
			
class Server(asyncore.dispatcher):

	def __init__(self, host, port):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind((host, port))
		self.listen(5)

	def handle_accept(self):
		pair = self.accept()
		if pair is None:
			pass
		else:
			sock, addr = pair
			print 'Incoming connection from %s' % repr(addr)
			handler = Handler(sock)

config = ConfigParser.ConfigParser()
config.read('config.ini')
server = Server(config.get('config','address'), int(config.get('config','port')))
asyncore.loop()

