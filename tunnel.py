import mysql.connector
import sshtunnel


_host = "192.168.8.1"   #Server where database is hosted
_ssh_port = 22   #ssh port
_username = "flights"  #user name to host server
_password = "nog3willy3" #password to ssh key
_remote_bind_address = "127.0.0.1"  #local connection IP to db on host(should probably not change)
_remote_mysql_port = 3306
_local_bind_address = "0.0.0.0"  #local bind address(should probably not change)
_local_mysql_port = 3306
_db_user = "flights"
_db_password = "nog3willy3"
_db_name = "flights"

with sshtunnel.SSHTunnelForwarder(
        (_host, _ssh_port),
        ssh_username=_username,
        ssh_password=_password,
        remote_bind_address=(_remote_bind_address, _remote_mysql_port),
        local_bind_address=(_local_bind_address,_local_mysql_port)
) as tunnel:
        connection = mysql.connector.connect(
                user=_db_user,
                passwd=_db_password,
                host=_local_bind_address,
                database=_db_name,
                port=_local_mysql_port)