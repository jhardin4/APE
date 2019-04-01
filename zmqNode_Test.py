from zmqNode import zmqNode
from multiprocessing import Process
import time
import threading

def ServerStart():
    serverlist = []
    servernode = zmqNode()
    servernode.connect('server', "tcp://127.0.0.1:5587", server=True)
    servernode.start_listening()

def timertest():
    print('still alive')
 

def main():
    
    server = Process(target=ServerStart)
    server.start()

    
    clientlist = []
    clientnode = zmqNode()
    clientnode.logfile = 'clientlog.txt'
    clientnode.connect('server', "tcp://127.0.0.1:5587")
    
    return_message = {'subject': 'node', 'action': 'zprint', 'dinfo': {'message': 'testing'}}
    message = {'ereply': return_message}

    for n in range(5):
        threading.Timer(n+1, clientnode.send, args=['server', message]).start()
        threading.Timer(n+1, clientnode.listen_once).start()
        threading.Timer(n+1, timertest).start()
        threading.Timer(n+1, print, args=[str(server.is_alive())]).start()
    threading.Timer(15, clientnode.close).start()
    close_message = {'subject': 'node', 'action': 'close'}
    threading.Timer(14, clientnode.send, args=['server', close_message]).start()
    threading.Timer(16, server.join).start()
    print(str(server.is_alive()))
    
if __name__ == '__main__':
    main()
    #ServerStart()