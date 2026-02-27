from Network_Automation_and_Operations.Init.AutoDev import *

if __name__ == "__main__":
    # ADConfig = AutoDevConfig()
    # ADConfig.ad_config_getstartfile()
    # ADConfig.AD_Config_Start_Stage()
    # ADConfig.AD_Config_Start_Stage(Change_Name=True,InitConfig_Backup=True)
    # ADConfig.AD_Config_Start_Stage(Change_Name=True)
    # ADConfig.AD_Config_Core()
    createconfig = AutoDevCreateConfig()
    createconfig.ad_createconfig_file()
