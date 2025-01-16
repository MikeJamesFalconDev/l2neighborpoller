
class Device:

    def __init__(self, ip):
        self.ip = ip
        self.hostname = ''
        self.neighbors = {}
        self.hosts = {}
        self.ifs = {}

    def assign_index(self, index):
        if index in self.hosts and index in self.ifs:
            self.neighbors[self.ifs[index]] = self.hosts[index]

    def add_if(self, index, value):
        self.ifs[index] = value
        self.assign_index(index)

    def add_host(self, index, value):
        self.hosts[index] = value
        self.assign_index(index)

    def print(self):
        print(f'{self.hostname}')
        print(f'\t{self.ip}')
        print('\tNeighbors:')
        for intf in self.neighbors:
            if intf in self.neighbors:
                print(f'\t\t{intf} -> {self.neighbors[intf]}')
            else:
                print(f'\t\t{intf}')
        print('\tInterfaces with no remote host')
        for intf in self.ifs.values():
            if intf not in self.neighbors:
                print(f'\t\t{intf}')
        print('\tHosts with no interface')
        for host in self.hosts.values():
            if host not in self.neighbors.values():
                print(f'\t\t{host}')

    def __str__(self):
        return f'{self.hostname} <-> {self.ip}'