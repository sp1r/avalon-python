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




class Handler(asyncore.dispatcher_with_send):

	def handle_read(self):
		data = self.recv(8192)
		if data:
			pop = subprocess.Popen(data.strip(), shell=True, cwd='/home/axeo/', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdin, stderr = pop.communicate()			
			self.send(stdin + stderr)
	
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

server = Server('localhost', 8080)
asyncore.loop()
