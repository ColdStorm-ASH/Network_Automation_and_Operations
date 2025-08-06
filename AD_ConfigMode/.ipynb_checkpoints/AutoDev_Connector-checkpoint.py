from Init.AutoDevTools import *
from Init.BaseTools import *
from AD_ConfigMode.AutoDev_SystemConfig import *
from AD_ConfigMode.AutoDev_IP_Route import *


class AutoDev_Connector:
    def __init__(self):
        self.ADOT = AutoDev_OtherTools()
        self.AD_SystemConfig = AutoDev_SystemConfig()
        self.ADIR = AutoDev_IP_Route()
        
    def ADC_Function_Call(self,parameter,mode="normal"):
        if mode == "init":
            init_command_list = self.AD_SystemConfig.ADSC_ChangeSystemName(parameter)
            print(init_command_list)
            return init_command_list
            
        elif mode == "normal":
            if parameter[0]['sheet_name'] == "Port_IP_Sheet(Router)":
                Config_dict = parameter[1]
                command_list = self.AD_SystemConfig.ADSC_Port_IP(Config_dict)
                print(command_list)
                return command_list

            elif parameter[0]['sheet_name'] == "IP_Route_Static_Sheet":
                IP_Route_Static_Config_list = parameter[1::]
                command_list = self.ADIR.ADIR_Static(IP_Route_Static_Config_list)
                print(command_list)
                return command_list
            
        
    