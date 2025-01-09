from snmp import Engine

from config import get_snmp_config

def get_oid(oids, host):
    config = get_snmp_config()
    if config['version'] != '1' and config['version'] != '2c':
        raise Exception(f'Invalid snmp version {config["version"]}. Currently supported 1 and 2c')
    with Engine() as engine:
        host = engine.Manager(host)
        return host.get(**oids)

def get_neighbors(host):
    config = get_snmp_config()
    neighbors = get_oid(config['oids'], host)
    print(f'device {host} neighbors: {neighbors}')
    return neighbors
