from Network_Automation_and_Operations.Init.AutoDevTools import *
from Network_Automation_and_Operations.Init.BaseTools import *



class AutoDev_SystemConfig:
    def __init__(self):
        self.ADOT = AutoDev_OtherTools()

    def ADSC_ConfigSave(self):
        # 构造保存命令
        pass
    
    def ADSC_ChangeSystemName(self, SystemName):
        # 构造 sysname命令
        command = ["sysname",SystemName]
        command_str = self.ADOT.ADOT_list_to_string(command)
        return [
            {"command":"system-view ","mode":"Quick","time":""},
            {"command":command_str,"mode":"Quick","time":""},
            {"command":"quit ","mode":"Recv","time":""}
        ]

    def ADSC_Port_IP(self,Config_dict):
        # Command_Standardization_list = [{"command": "system-view ", "mode": "Quick", "time": ""}]
        Command_Standardization_list = []
        for Port_Num,IP_And_Mask in Config_dict.items():
            result,Port_IP,IP_Mask = self.ADOT.ADOT_Check_IP_And_Mask_Sparate(IP_And_Mask)

            if result:
                # 构造 interface 命令
                interface_command = ["interface", Port_Num]
                interface_command_str = self.ADOT.ADOT_list_to_string(interface_command)

                # 构造 ip address 命令
                ip_command = ["ip", "address", Port_IP, IP_Mask]
                ip_command_str = self.ADOT.ADOT_list_to_string(ip_command)
                
                # 按顺序添加三条命令到列表
                Command_Standardization_list.append({
                    "command": interface_command_str,
                    "mode": "Quick",
                    "time": ""
                })
                Command_Standardization_list.append({
                    "command": ip_command_str,
                    "mode": "Quick",
                    "time": ""
                })
                Command_Standardization_list.append({
                    "command": "quit ",
                    "mode": "Recv",
                    "time": ""
                })
                
        return Command_Standardization_list

    
class AutoDev_ConfigCommandCreate:
    def __init__(self):
        self.ADOT = AutoDev_OtherTools()   
    
    def AD3C_BaseService(self,SystemName):
        pass

    def AD3C_BaseServoce(self):
        pass





"""
# 改名操作
sysname XXXX

# console密码配置
user-interface aux 0
authentication-mode password
user-role level-15
user-role network-admin
set authentication password simple H3C@123
quit

# telnet和ssh配置
ssh server enable
telnet server enable
local-user user class manage 
password simple User@12345
service-type telnet ssh
authorization-attribute use networ-admin
authorization-attribute user-role level-15
quit
line vty 0 15 
authentication-mode scheme 
protocol inbound all
quit

# snmp配置
snmp-agent sys-info version all
snmp-agent community read public
snmp-agent community write private




"""


