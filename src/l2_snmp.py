from snmp import Engine, SNMPv1, SNMPv2c

from config import get_snmp_config

def get_oid(oids, host):
    config = get_snmp_config()
    if config['version'] != '1' and config['version'] != '2c':
        raise Exception(f'Invalid snmp version {config["version"]}. Currently supported 1 and 2c')
    value = None
    with Engine() as engine:
        version = SNMPv2c if config['version'] != '2c' else SNMPv1
        host = engine.Manager(host, version=version)
        for oid in oids:
            try:
                value = host.get(oid)
            except Exception as e:
                print(f'{oid} failed for {host}. {e}')
                continue
            print(f'{oid} = {value}') 
        return value

def get_neighbors(host):
    print(f'Getting neighbors for {host}')
    config = get_snmp_config()
    neighbors = get_oid(config['oids'], host)
    print(f'Neighbors: {neighbors}')
    return neighbors
