import toml

CONFIG_FILE = 'config.toml'

def get_config():
    return toml.load(CONFIG_FILE)

def get_devices_db_config():
    return get_config()['db_devices']

def get_topology_db_config():
    return get_config()['db_topology']

def get_snmp_config():
    return get_config()['snmp']