#!/usr/bin/env python3
# coding=utf-8

import socket
import select
import queue

server = socket.socket()
server.setblocking(False)
server.bind(('0.0.0.0', 8888))
server.listen()

epoll = select.epoll()
epoll.register(server.fileno(), select.EPOLLIN)

message_queue = {}
connections = {}
while True:
    events = epoll.poll()
    for fileno, event in events:
        if fileno == server.fileno():
            conn, address = server.accept()
            print('connected from', conn.getpeername())
            conn.setblocking(False)
            epoll.register(conn.fileno(), select.EPOLLIN)
            connections[conn.fileno()] = conn
            message_queue[conn.fileno()] = queue.Queue()
        elif event & select.EPOLLIN:
            conn = connections[fileno]
            data = conn.recv(1024)
            if data:
                data_str = data.decode()
                print('data recv from %s: %s' % (conn.getpeername(), data_str))
                message_queue[fileno].put(data_str)
                epoll.modify(fileno, select.EPOLLIN | select.EPOLLOUT)
            else:
                print('disconnected from', conn.getpeername())
                conn.close()
                epoll.modify(fileno, 0)
                del message_queue[fileno]
                del connections[fileno]
        elif event & select.EPOLLOUT:
            if not message_queue[fileno].empty():
                data = message_queue[fileno].get()
                conn = connections[fileno]
                print('send %s to %s' % (data, conn.getpeername()))
                conn.sendall(data.encode())
            else:
                epoll.modify(fileno, select.EPOLLIN)
        elif event & select.EPOLLHUP:
            conn = connections[fileno]
            print('disconnected from', conn.getpeername())
            epoll.unregister(fileno)
            del message_queue[fileno]
            del connections[fileno]


