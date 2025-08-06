from Init.AutoDevTools import *
from Init.BaseTools import *



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



