from db import get_devices_ips, insert_neighbors
from asyncio import *

from l2_snmp import get_neighbors, get_sysname
from config import get_snmp_config
from device import Device

devices = {}

async def main():
    config = get_snmp_config()
    tasks = []
    devices_ips = get_devices_ips()
    for ip in devices_ips:
        task = create_task(get_sysname(ip, config, devices))
        tasks.append(task)
    await gather(*tasks)

    for device in devices.values():
        task = create_task(get_neighbors(device, config, devices))
        tasks.append(task)
    await gather(*tasks)

    for device in devices.values():
        device.print()
        insert_neighbors(device)

if __name__ == "__main__":
    run(main())