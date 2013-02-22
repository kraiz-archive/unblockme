class Validator(object):
    def __init__(self, clients):
        self.clients = clients

    def is_valid(self, ip, domain):
        return ip in self.clients
