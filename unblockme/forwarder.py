import gevent
import socket


class DuplexForwarder(gevent.Greenlet):
    """gevent based helper forwarding traffic back and forth"""

    def __init__(self, source, dest, buffer_size, timeout):
        self.buffer_size = buffer_size
        self.timeout = timeout
        self.source = source
        self.dest = dest
        gevent.Greenlet.__init__(self)

    def _run(self):
        gevent.spawn(self.handle, self.source, self.dest)
        gevent.spawn(self.handle, self.dest, self.source)

    def handle(self, source, dest):
        try:
            source.settimeout(self.timeout)
            while True:
                data = source.recv(self.buffer_size)
                if not data:
                    break
                dest.sendall(data)
        except socket.error:
            pass
        finally:
            self.source.close()
            self.dest.close()
