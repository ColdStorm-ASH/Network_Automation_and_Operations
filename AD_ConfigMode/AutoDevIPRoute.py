from Network_Automation_and_Operations.Init.AutoDevTools import *
from Network_Automation_and_Operations.Init.BaseTools import *

class AutoDevIPRoute:
    def __init__(self):
        self.ADOT = AutoDevOtherTools()
        

    def adir_static(self, IP_Route_Static_Config_list):
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
            route_command_str = self.ADOT.adot_list_to_string(cmd_parts)
            # print(route_command_str)
    
            # 返回命令列表（带模式）
            
            Command_Standardization_list.append({
                "command": route_command_str,
                "mode": "Quick",
                "time": ""
            })

        Command_Standardization_list.append({"command": "quit ", "mode": "Recv", "time": ""})
    
        return Command_Standardization_list

    def adir_static_config(self, ip_route_static_config_list):
        command_standardization_list = []

        for item in ip_route_static_config_list:
            # 提取字段
            des_network = item.get("Des_Network")
            mask = item.get("Mask")
            nexthop_ip = item.get("Next-hop_IP")  # 注意键名中的连字符
            nexthop_port = item.get("Next-hop_Port")
            preference = item.get("Preference")

            cmd_parts = ["ip route-static", des_network, mask]

            if nexthop_port != None:
                cmd_parts.append(nexthop_port)

            cmd_parts.append(nexthop_ip)

            if preference != None:
                cmd_parts.append(preference)

            # 拼接完整命令
            route_command_str = self.ADOT.adot_list_to_string(cmd_parts)
            # print(route_command_str)

            # 返回命令列表（带模式）

            command_standardization_list.append(route_command_str)
            # print(f"方法内输出{command_standardization_list}")

        return command_standardization_list


    def adir_ospf_base(self, Router_ID, ):
        pass