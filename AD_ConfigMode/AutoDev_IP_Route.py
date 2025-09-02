from Network_Automation_and_Operations.Init.AutoDevTools import *
from Network_Automation_and_Operations.Init.BaseTools import *

class AutoDev_IP_Route:
    def __init__(self):
        self.ADOT = AutoDev_OtherTools()
        

    def ADIR_Static(self, IP_Route_Static_Config_list):
        # Command_Standardization_list = [{"command": "system-view ", "mode": "Quick", "time": ""}]
        Command_Standardization_list = []

        for item in IP_Route_Static_Config_list:
            # 提取字段
            Des_Network = item.get("Des_Network")
            Mask = item.get("Mask")
            NextHop_IP = item.get("Next-hop_IP")  # 注意键名中的连字符
            NextHop_Port = item.get("Next-hop_Port")
            Preference = item.get("Preference")
            
            cmd_parts = ["ip route-static", Des_Network, Mask]
    
            if NextHop_Port != None:
                cmd_parts.append(NextHop_Port)
    
            cmd_parts.append(NextHop_IP)
    
            if Preference != None:
                cmd_parts.append(Preference)
    
            # 拼接完整命令
            route_command_str = self.ADOT.ADOT_list_to_string(cmd_parts)
            # print(route_command_str)
    
            # 返回命令列表（带模式）
            
            Command_Standardization_list.append({
                "command": route_command_str,
                "mode": "Quick",
                "time": ""
            })

        Command_Standardization_list.append({"command": "quit ", "mode": "Recv", "time": ""})
    
        return Command_Standardization_list


    def ADIR_OSPF_Base(self, Router_ID, ):
        pass