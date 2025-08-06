from Init.AutoDev import *

if __name__ == "__main__":
    ADConfig = AutoDev_Config()
    ADConfig.AD_Config_GetStartFile()
    ADConfig.AD_Config_Start_Stage()
    # ADConfig.AD_Config_Start_Stage(Change_Name=True,InitConfig_Backup=True)
    # ADConfig.AD_Config_Start_Stage(Change_Name=True)
    ADConfig.AD_Config_Core()