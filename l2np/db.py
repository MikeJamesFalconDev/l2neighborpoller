import mysql.connector
import psycopg2
import getpass
import subprocess

from config import get_devices_db_config, get_topology_db_config

def clean_db_config(config):
    clean_config = {**config}
    del clean_config["type"]
    if "table" in clean_config:
        del clean_config["table"]
    del clean_config["ip_field"]
    if "neighbor_field" in clean_config:
        del clean_config["neighbor_field"]
    if "query" in clean_config:
        del clean_config["query"]
    return clean_config

def get_connection_postgresql(config):
    psql_config = clean_db_config(config)
    return psycopg2.connect(**psql_config)

def get_connection_mysql(config):
    mysql_config = clean_db_config(config)
    return  mysql.connector.connect(**mysql_config)


get_connection_objects = {'postgresql': get_connection_postgresql, 'mysql': get_connection_mysql}

def get_connection(config):
    if config['type'] in get_connection_objects:
        return get_connection_objects[config['type']](config)

def close(conn):
    conn.close()

def query(sql, conn):
    cursor = conn.cursor()
    cursor.execute(sql)
    return [dict(zip([column[0] for column in cursor.description], row))
             for row in cursor.fetchall()]

def get_devices():
    ips = []
    config = get_devices_db_config()
    with get_connection(config) as conn:
        for entry in query(config['query'], conn):
            if (config['ip_field'] in entry):
                ips.append(entry[config['ip_field']])
    print(f'Found devices:\n{ips}')
    return ips

def insert_neighbors(ip, neighbors):
    config = get_topology_db_config()
    with get_connection(config) as conn:
        for neighbor in neighbors:
            query(f'insert into {config["table"]} ({config["ip_field"]}, {config["neighbor_field"]}) values ({ip}, {neighbor})', conn)

def main():
    """Creates the database and table to store the output generated by the script using the configuration in config.toml file.
        Must be run as root. Only works for local database"""
    config = get_topology_db_config()
    if config['host'] == '127.0.0.1' or config['host'] == 'localhost':
        os_user = getpass.getuser()
        if  os_user == 'root':
            if config['type'] == 'mysql':
                sql = f'create user if not exists \'{config["user"]}\'@\'{config["host"]}\' identified by \'{config["password"]}\';'
                print('Creating user')
                print(sql)
                subprocess.run(['mysql', f'--execute={sql}'])

                sql = f'create database if not exists {config["db"]};'
                print('Creating database')
                print(sql)
                subprocess.run(['mysql', f'--execute={sql}'])
                
                sql = f'GRANT ALL PRIVILEGES ON {config["db"]}.* TO \'{config["user"]}\'@\'{config["host"]}\';FLUSH PRIVILEGES;'
                print('Adding privileges')
                print(sql)
                subprocess.run(['mysql', f'--execute={sql}'])
            else:
                pass
        else:
            print(f'DB user is only created automatically when run as root and host is localhost. Current user \'{os_user}\'')
    else:
        print(f'DB user is only created automatically when run as root and host is localhost. Current host \'{config["host"]}\'')

    with get_connection_mysql(config) as conn:
        print('Creating table')
        sql = f'create table if not exists {config["table"]} ({config["ip_field"]} varchar(25), {config["neighbor_field"]} varchar(25), primary key ({config["ip_field"]}))'
        print(sql)
        query(sql, conn)


if __name__ == "__main__":
    main()