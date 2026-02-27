from Network_Automation_and_Operations.Init.AutoDevTools import *
from Network_Automation_and_Operations.Init.BaseTools import *


class AutoDevSystemConfig:
    def __init__(self):
        self.ADOT = AutoDevOtherTools()

    def adsc_configsave(self):
        # 构造保存命令
        pass
    
    def adsc_changesystemname(self, SystemName):
        # 构造 sysname命令
        command = ["sysname",SystemName]
        command_str = self.ADOT.adot_list_to_string(command)
        return [
            {"command":"system-view ","mode":"Quick","time":""},
            {"command":command_str,"mode":"Quick","time":""},
            {"command":"quit ","mode":"Recv","time":""}
        ]

    def adsc_port_ip(self,Config_dict):
        # Command_Standardization_list = [{"command": "system-view ", "mode": "Quick", "time": ""}]
        Command_Standardization_list = []
        for Port_Num,IP_And_Mask in Config_dict.items():
            result,Port_IP,IP_Mask = self.ADOT.adot_check_ip_and_mask_sparate(IP_And_Mask)

            if result:
                # 构造 interface 命令
                interface_command = ["interface", Port_Num]
                interface_command_str = self.ADOT.adot_list_to_string(interface_command)

                # 构造 ip address 命令
                ip_command = ["ip", "address", Port_IP, IP_Mask]
                ip_command_str = self.ADOT.adot_list_to_string(ip_command)
                
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

    
class AutoDevConfigCommandCreate:
    def __init__(self):
        self.ADOT = AutoDevOtherTools()

    def ad3c_system_init_config(self, parameter,device_sysname=None, config_options=None):
        """
        根据 Init_Sheet 配置数据生成系统初始化配置命令

        Args:
            parameter: 配置数据列表，格式为 [
                {'sheet_name': 'Init_Sheet'},
                {'Manage_IP': 'xxx', 'Manager_Name': 'xxx', 'Manager_Password': 'xxx'}
            ]
            config_options: 配置开关字典（可选），支持以下键：
                - enable_console: 是否配置 console（默认 True）
                - enable_ssh_telnet: 是否配置 SSH/Telnet（默认 True）
                - enable_snmp: 是否配置 SNMP（默认 True）
                - enable_sysname: 是否配置系统名称（默认 True）
                - console_password: console 默认密码（默认 'H3C@123'）
                - snmp_read_community: SNMP 读团体名（默认 'public'）
                - snmp_write_community: SNMP 写团体名（默认 'private'）

        Returns:
            command_standardization_list: 标准化命令列表
        """
        command_standardization_list = []
        # print(parameter)

        # 配置开关map
        default_options = {
            'enable_console': True,
            'enable_ssh_telnet': True,
            'enable_snmp': True,
            'enable_sysname': True,
            'console_password': 'H3C@123.com',
            'snmp_read_community': 'public',
            'snmp_write_community': 'private'
        }

        # 合并用户传入的配置开关（用户传入的覆盖默认值）
        if config_options is None:
            config_options = {}
        options = {**default_options, **config_options}

        # 验证参数
        if not isinstance(parameter, list) or len(parameter) < 1:
            print("❌ 错误：parameter 必须是包含至少 1 个元素的列表")
            return command_standardization_list

        config_dict = parameter[0]
        manage_ip = config_dict.get('Manage_IP', '')
        manager_name = config_dict.get('Manager_Name', '')
        manager_password = config_dict.get('Manager_Password', '')

        # 验证账户密码
        has_auth_config = True
        if not manager_name:
            print("⚠️  警告：Manager_Name 为空，不进行账户密码配置")
            has_auth_config = False
        if not manager_password:
            print("⚠️  警告：Manager_Password 为空，不进行账户密码配置")
            has_auth_config = False

        # 系统名称配置
        if device_sysname != None:
            change_system_name_command = ["sysname", device_sysname]
            change_system_name_command_str = self.ADOT.adot_list_to_string(change_system_name_command)
            command_standardization_list.append(change_system_name_command_str)
        else:
            sysname = "Device" + manage_ip
            change_system_name_command = ["sysname", sysname]
            change_system_name_command_str = self.ADOT.adot_list_to_string(change_system_name_command)
            command_standardization_list.append(change_system_name_command_str)

        # Console 密码配置
        if options['enable_console']:
            command_standardization_list.extend([
                "user-interface aux 0",
                "authentication-mode password",
                "user-role level-15",
                "user-role network-admin"
            ])

            # 有账户密码则使用传入的，否则使用默认密码
            if has_auth_config:
                console_pwd = manager_password
            else:
                console_pwd = options['console_password']
                print(f"ℹ️  使用默认 console 密码：{console_pwd}")

            console_auth_password_command = ["set authentication password simple", console_pwd]
            console_auth_password_command_str = self.ADOT.adot_list_to_string(console_auth_password_command)
            command_standardization_list.append(console_auth_password_command_str)
            command_standardization_list.append("quit")

        # Telnet 和 SSH 配置
        if options['enable_ssh_telnet']:
            command_standardization_list.extend([
                "ssh server enable",
                "telnet server enable"
            ])

            if has_auth_config:
                command_standardization_list.extend([
                    f"local-user {manager_name} class manage",
                    f"password simple {manager_password}",
                    "service-type telnet ssh",
                    "authorization-attribute user-role network-admin",
                    "authorization-attribute user-role level-15",
                    "quit"
                ])

            command_standardization_list.extend([
                "line vty 0 15",
                "authentication-mode scheme",
                "protocol inbound all",
                "quit"
            ])

        # SNMP 配置
        if options['enable_snmp']:
            command_standardization_list.extend([
                "snmp-agent sys-info version all",
                f"snmp-agent community read {options['snmp_read_community']}",
                f"snmp-agent community write {options['snmp_write_community']}"
            ])

        # print(command_standardization_list)

        return command_standardization_list

    def ad3c_l3port_config(self,config_dict):
        command_standardization_list = []
        # print(config_dict)
        for port_num,ip_and_mask in config_dict.items():
            result,ip,mask = self.ADOT.adot_check_ip_and_mask_sparate(ip_and_mask)
            if result:
                # 构造 interface 命令
                interface_command = ["interface", port_num]
                interface_command_str = self.ADOT.adot_list_to_string(interface_command)
                command_standardization_list.append(interface_command_str)

                # 构造 ip address 命令
                ip_command = ["ip", "address", ip, mask]
                ip_command_str = self.ADOT.adot_list_to_string(ip_command)
                command_standardization_list.append(ip_command_str)
                command_standardization_list.append("quit")

        return command_standardization_list

    def ad3c_l2port_config(self, config_dict):
        pass

    def ad3c_baseservice(self):
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


