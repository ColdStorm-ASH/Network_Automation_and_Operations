from Network_Automation_and_Operations.AD_ConfigMode.AutoDevIPRoute import *
from Network_Automation_and_Operations.AD_ConfigMode.AutoDevSystemConfig import *
from Network_Automation_and_Operations.Init.BaseTools import *


class AutoDevConnector:
    def __init__(self) -> None:
        self.ADOT = AutoDevOtherTools()
        self.AD_SystemConfig = AutoDevSystemConfig()
        self.ADIR = AutoDevIPRoute()

        self.AD3C = AutoDevConfigCommandCreate()

    # """ 过渡方法 """
    # def adc_function_call(self,parameter,mode="normal"):
    #     """
    #     AutoDev_Function_Call是AutoDev_Connector类的核心方法。用于将接驳器接收到的标准化好的参数分类到对应的方法下执行。
    #     :param parameter:
    #     :param mode:
    #     :return:
    #     """
    #     if mode == "init":
    #         """
    #         用于开局基础
    #         """
    #         init_command_list = self.AD_SystemConfig.adsc_changesystemname(parameter)
    #         print(init_command_list)
    #         return init_command_list
    #
    #     elif mode == "normal":
    #         """
    #         用于正常模式下的方法调用
    #         该elif下，在数量少的情况下可以通过if的方法来进行调用，如果数量多的情况，建议改造使用字典构造一个map进行方法调用。
    #         """
    #         if parameter[0]['sheet_name'] == "Port_IP_Sheet(Router)":
    #             Config_dict = parameter[1]
    #             command_list = self.AD_SystemConfig.adsc_port_ip(Config_dict)
    #             # print(command_list)
    #             return command_list
    #
    #         elif parameter[0]['sheet_name'] == "IP_Route_Static_Sheet":
    #             IP_Route_Static_Config_list = parameter[1::]
    #             command_list = self.ADIR.adir_static(IP_Route_Static_Config_list)
    #             # print(command_list)
    #             return command_list
    #
    #     elif mode == "Engineering_Test":
    #         """
    #         保留：用于工程测试
    #         """
    #         print("Engineering_Test")
    #
    #     elif mode == "OP":
    #         """
    #         用于运维方法
    #         """
    #         print("OP")
    #     """ 过渡方法 """


    def adc_function_call(self,parameter,mode="normal",sysname=None):
        """
        adc_function_call是AutoDev_Connector类的核心方法。用于将接驳器接收到的标准化好的参数分类到对应的方法下执行。
        此方法为adc_function_call的改进写法，加入了function map对想要调用的方法进行查找。
        :param sysname:
        :param parameter:
        :param mode:
        :return:
        """
        if mode == "init":
            """
            用于开局基础
            """
            init_command_list = self.AD_SystemConfig.adsc_changesystemname(parameter)
            print(init_command_list)
            return init_command_list

        elif mode == "normal":
            """
            用于正常模式下的方法调用
            该elif下，在数量少的情况下可以通过if的方法来进行调用，如果数量多的情况，建议改造使用字典构造一个map进行方法调用。
            """
            if parameter[0]['sheet_name'] == "Port_IP_Sheet(Router)":
                Config_dict = parameter[1]
                command_list = self.AD_SystemConfig.adsc_port_ip(Config_dict)
                # print(command_list)
                return command_list

            elif parameter[0]['sheet_name'] == "IP_Route_Static_Sheet":
                IP_Route_Static_Config_list = parameter[1::]
                command_list = self.ADIR.adir_static(IP_Route_Static_Config_list)
                # print(command_list)
                return command_list

        elif mode == "create_config_command":
            print(f"✅ 已启用自动配置生成接驳模块，模式为：{mode}")
            # print(parameter)

            # 定义映射配置
            sheet_method_map = {
                "IP_Route_Static_Sheet": (self.ADIR, "adir_static_config", "list"),
                "Port_IP_Sheet(Router)": (self.AD3C, "ad3c_l3port_config", "single"),
                "Init_Sheet": (self.AD3C, "ad3c_system_init_config", "init"),
            }

            # 验证参数
            if not parameter or not isinstance(parameter, list):
                raise TypeError("parameter 必须是列表类型")

            if len(parameter) < 1 or 'sheet_name' not in parameter[0]:
                raise ValueError("parameter 第一个元素必须包含 'sheet_name' 键")

            # 获取 sheet_name
            sheet_name = parameter[0].get('sheet_name')

            # 查找映射配置
            if sheet_name not in sheet_method_map:
                available_sheets = ", ".join(sheet_method_map.keys())
                raise ValueError(
                    f"未找到 sheet_name '{sheet_name}' 对应的处理方法。\n"
                    f"可用的 sheet_name: {available_sheets}"
                )

            # 从 map 中解包出 instance、method_name、param_type
            instance, method_name, param_type = sheet_method_map[sheet_name]

            # 检查实例是否有该方法
            if not hasattr(instance, method_name):
                raise AttributeError(
                    f"类 {instance.__class__.__name__} 中不存在方法 '{method_name}'"
                )

            # 获取方法对象
            method = getattr(instance, method_name)

            # 准备参数
            if param_type == "single":
                config_data = parameter[1] if len(parameter) > 1 else {}
            elif param_type == "list":
                config_data = parameter[1:]
            elif param_type == "init":
                config_data = [parameter[1]] if len(parameter) > 1 else [{}]

            # print(f"{method_name}")
            # print(type(method_name))
            # 调用方法
            if method_name != "ad3c_system_init_config":
                # print(f"{method_name}")
                command_list = method(config_data)
                print(f"✅ 已处理 {sheet_name}，调用方法：{instance.__class__.__name__}.{method_name}")

            elif method_name == "ad3c_system_init_config":
                if sysname:
                    # print(f"{method_name}")
                    # print(f"sysname:True")
                    command_list = method(config_data,device_sysname=sysname)
                else:
                    # print(f"{method_name}")
                    # print(f"sysname:False")
                    command_list = method(config_data)
                print(f"✅ 已处理 {sheet_name}，调用方法：{instance.__class__.__name__}.{method_name}")
            else:
                print(f"方法调用错误")
                command_list = []

            # print(command_list)

            return command_list


            # route_configs = [item for item in data if item.get('sheet_name') == 'IP_Route_Static_Sheet']

        elif mode == "Engineering_Test":
            """
            保留：用于工程测试
            """
            print("Engineering_Test")

        elif mode == "OP":
            """
            用于运维方法
            """
            print("OP")
