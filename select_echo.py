#!/usr/bin/env python3
# coding=utf-8

import socket
import select
import queue

server = socket.socket()
server.setblocking(False)
server.bind(('0.0.0.0', 8888))
server.listen()

message_queue = {}
rlist = {server}
wlist = set()

while True:
    readable, writable, exceptional = select.select(rlist, wlist, rlist)
    for rsocket in readable:
        if rsocket is server:
            conn, addr = rsocket.accept()
            print('connected from', conn.getpeername())
            rlist.add(conn)
            message_queue[conn] = queue.Queue()
        else:
            data = rsocket.recv(1024)
            if data:
                data_str = data.decode()
                print('data recv from %s: %s' % (rsocket.getpeername(), data_str))
                message_queue[rsocket].put(data_str)
                if rsocket not in wlist:
                    wlist.add(rsocket)
            else:
                print('disconnected from', rsocket.getpeername())
                rlist.remove(rsocket)
                rsocket.close()
                del message_queue[rsocket]

    for wsocket in writable:
        if not message_queue[wsocket].empty():
            data = message_queue[wsocket].get()
            print('send %s to %s' % (data, wsocket.getpeername()))
            wsocket.sendall(('echo: ' + data).encode())
        else:
            print('empty message queue:', wsocket.getpeername())
            wlist.remove(wsocket)
