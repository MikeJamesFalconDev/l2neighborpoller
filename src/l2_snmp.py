from snmp import Engine, SNMPv1, SNMPv2c
from snmp.pdu import NoSuchObject, NoSuchInstance
from pysnmp.hlapi.v3arch.asyncio import *
from pprint import pprint

from device import Device

# def get_oid(oids, host):
#     config = get_snmp_config()
#     if config['version'] != '1' and config['version'] != '2c':
#         raise Exception(f'Invalid snmp version {config["version"]}. Currently supported 1 and 2c')
#     value = None
#     community = config['community'].encode('utf-8')
#     with Engine() as engine:
#         version = SNMPv2c if config['version'] == '2c' else SNMPv1
#         host = engine.Manager(host, version=version, community=community)
#         for oid in oids:
#             try:
#                 value = host.get(oid)
#                 value = value.__getitem__(0).value
#                 if value == NoSuchObject():
#                     print(f'Unknown OID {oid}')
#                     value = None
#                     continue
#                 if value == NoSuchInstance():
#                     print(f'No value for OID {oid}')
#                     value = None
#                     continue
#             except Exception as e:
#                 print(f'{oid} failed for {host}. {type(e).__name__}')
#                 continue
#             print(f'{oid} = {value}') 
#         return value

snmpVersions = { '1': 0, '2c': 1 }

async def get_value(host, oid, community, version):
    snmpEngine = SnmpEngine()
    response = get_cmd(
        snmpEngine,
        CommunityData(community, mpModel=snmpVersions[version]),
        await UdpTransportTarget.create((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )

    errorIndication, errorStatus, errorIndex, varBinds = await response

    if errorIndication:
            print(f'Error indication for {oid} on {host}. {errorIndication}')
    elif errorStatus:
        print(f'Error status for {oid} on {host}. {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or "?"}')
    else:
        return varBinds[0][1].prettyPrint()

    snmpEngine.close_dispatcher()



async def get_list(host, oid, community, version):
    snmpEngine = SnmpEngine()
    
    response = walk_cmd(
        snmpEngine,
        CommunityData(community, mpModel=snmpVersions[version]),
        await UdpTransportTarget.create((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False,
        lookupMib=False
    )

    async for errorIndication, errorStatus, errorIndex, varBinds in response:
        if errorIndication:
            print(f'Error indication for {oid} on {host}. {errorIndication}')
        elif errorStatus:
            print(f'Error status for {oid} on {host}. {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or "?"}')
        else:
            for varBind in varBinds:
                out_oid = varBind[0].prettyPrint()
                value = varBind[1].prettyPrint()
                yield (out_oid, value)
    snmpEngine.close_dispatcher()

async def assign_neighbors(device: Device,devices, neighbors, lldp):
    got_values = False
    host_oid = lldp['neighbors'] + lldp['host']
    if_oid = lldp['neighbors'] + lldp['interface']
    async for neighbor in neighbors:
        oid = neighbor[0]
        value = neighbor[1]
        if value.strip() == '':
            continue
        if oid.startswith(host_oid):
            if value in devices.keys():
                neighbor_device = devices[value]
            else:
                # print(f'Hostname {value} not found')
                neighbor_device = Device('Empty')
                neighbor_device.hostname = value
            device.add_host(oid.replace(host_oid, ''), neighbor_device)
            got_values = True
        elif oid.startswith(if_oid):
            device.add_if(oid.replace(if_oid, ''), value)
            got_values = True
    return got_values

async def get_sysname(ip, config, devices):
    oid = config['sysname_oid']
    community = config['community']
    version = config['version']
    device = Device(ip)
    device.hostname = await get_value(ip, oid, community, version)
    # print(f'{ip} -> {device.hostname}')
    devices[device.hostname] = device

async def get_neighbors(device: Device, config, devices):
    community = config['community']
    version = config['version']
    neighbors = []
    for lldp in config['lldp']:
        neighbors = get_list(device.ip, lldp['neighbors'], community, version)
        if await assign_neighbors(device, devices, neighbors, lldp):
            break
