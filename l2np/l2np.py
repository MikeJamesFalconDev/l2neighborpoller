from db import get_devices, insert_neighbors
from l2_snmp import get_neighbors

def main():
    for ip in get_devices():
        insert_neighbors(ip, get_neighbors(ip))

if __name__ == "__main__":
    main()