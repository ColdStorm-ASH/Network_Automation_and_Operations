import paramiko
import time

ip = "192.168.56.3"
user = "user"
password = "User@12345"

# 实例化SSHclient
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=ip,username=user,password=password)
time.sleep(2)

command = ssh_client.invoke_shell()
command.send("dis version\n")

time.sleep(2)
output = command.recv(65535)
print(output.decode("ascii"))

ssh_client.close()