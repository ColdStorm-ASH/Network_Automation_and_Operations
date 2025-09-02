from Network_Automation_and_Operations.AD_ConfigMode.AutoDev_IP_Route import *
from Network_Automation_and_Operations.AD_ConfigMode.AutoDev_SystemConfig import *
from Network_Automation_and_Operations.Init.AutoDevTools import *
from Network_Automation_and_Operations.Init.BaseTools import *


class AutoDev_Connector:
    def __init__(self) -> None:
        self.ADOT = AutoDev_OtherTools()
        self.AD_SystemConfig = AutoDev_SystemConfig()
        self.ADIR = AutoDev_IP_Route()
        
    def ADC_Function_Call(self,parameter,mode="normal"):
        """
        AutoDev_Function_Call是AutoDev_Connector类的核心方法。用于将接驳器接收到的标准化好的参数分类到对应的方法下执行。
        :param parameter:
        :param mode:
        :return:
        """
        if mode == "init":
            """
            用于开局基础
            """
            init_command_list = self.AD_SystemConfig.ADSC_ChangeSystemName(parameter)
            print(init_command_list)
            return init_command_list
            
        elif mode == "normal":
            """
            用于正常模式下的方法调用
            该elif下，在数量少的情况下可以通过if的方法来进行调用，如果数量多的情况，建议改造使用字典构造一个map进行方法调用。
            """
            if parameter[0]['sheet_name'] == "Port_IP_Sheet(Router)":
                Config_dict = parameter[1]
                command_list = self.AD_SystemConfig.ADSC_Port_IP(Config_dict)
                # print(command_list)
                return command_list

            elif parameter[0]['sheet_name'] == "IP_Route_Static_Sheet":
                IP_Route_Static_Config_list = parameter[1::]
                command_list = self.ADIR.ADIR_Static(IP_Route_Static_Config_list)
                # print(command_list)
                return command_list

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
            
        
    