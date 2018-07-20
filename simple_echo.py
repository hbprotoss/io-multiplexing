#!/usr/bin/env python3
# coding=utf-8

import socket

SOCKET_FAMILY = socket.AF_INET
SOCKET_TYPE = socket.SOCK_STREAM

sockServer = socket.socket(SOCKET_FAMILY, SOCKET_TYPE)
sockServer.bind(('0.0.0.0', 8888))
sockServer.listen()

while True:
    conn, address = sockServer.accept()
    print('connected from', conn.getpeername())
    while True:
        data = conn.recv(1024)
        if data:
            print('data recv:', data.decode())
            conn.sendall("echo: ".encode() + data)
        else:
            conn.close()
            print('disconnected from', conn.getpeername())
            break

