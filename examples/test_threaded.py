import socket
import threading
from Queue import *
import SocketServer
import time

from socketpool.pool import ConnectionPool
from socketpool.conn import SocketConnector

class EchoHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        while True:
            data = self.request.recv(1024)
            if not data:
                break
            self.request.send(data)
            print ("echoed %r" % data)

class EchoServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0

    server = EchoServer((HOST, PORT), EchoHandler)
    ip, port = server.server_address


    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name

    options = {'host': ip, 'port': port}
    pool = ConnectionPool(factory=SocketConnector, options=options)
    q = Queue()

    def runpool():
        while True:
            try:
                data = q.get(False)
            except Empty:
                break
            print 'ok'
            try:
                with pool.connection() as conn:
                    print 'sending'
                    sent = conn.send(data)
                    print 'send %d bytes' % sent
                    echo = conn.recv(1024)
                    print "got %s" % data
                    assert data == echo
            finally:
                q.task_done()

    for i in xrange(20):
        q.put("Hello World %s" % i)

    threads = []
    for i in range(4):
        th = threading.Thread(target=runpool)
        th.daemnon = True
        th.start()
        threads.append(th)

    queue.join()

    server.shutdown()
