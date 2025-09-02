from Network_Automation_and_Operations.Init.AutoDevTools import *
from Network_Automation_and_Operations.Init.BaseTools import *
# from Network_Automation_and_Operations.AD_ConfigMode.AutoDev_SystemConfig import *
from Network_Automation_and_Operations.AD_ConfigMode.AutoDev_Connector import *
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class AutoDev_Config:
    """
    AutoDev_Config类用于自动化配置
    
    """
    def __init__(self,target_file_name="Automated_Configuration_Table_Template.xlsx"):

        # 构造参数
        self.target_file_name = target_file_name
        
        # 实例化基础工具类和数据表工具类
        self.ADOT = AutoDev_OtherTools()
        self.ADST = AutoDev_SheetTools()
        self.ADTT = AutoDev_TestTools()
        # self.AD_SystemConfig = AutoDev_SystemConfig()
        self.ADC = AutoDev_Connector()

        # 获取当前路径并构造配置表目录的绝对路径
        self.config_sheet_dir = self.ADOT.ADOT_GetAndCreat_contents("Config_Sheet")

        # 构造配置表绝对路径        
        self.target_file_path = os.path.join(self.config_sheet_dir, self.target_file_name)

        # 检查配置表是否存在，如果存在的话，导出配置表的表格名字。
        if self.ADOT.ADOT_Check_File(self.target_file_path):
            self.sheet_names = self.ADST.ADST_get_sheet_names(self.target_file_path)

        else:
            print("error")

    def AD_Config_GetStartFile(self):
        if "Init_Sheet" in self.sheet_names:
            Init_Sheet_dict = self.ADST.ADST_Export_Init_Sheet_dict(self.target_file_path)
        else:
            print(f"error:{self.target_file_path}该文件中没有Init_Sheet进行初始化")

        # 针对初始化表格文件进行处理，并生成临时文件。
        self.ADST.ADST_Init_Sheet_dict_Save_as_json_temp(self.target_file_path)

    def AD_Config_GetConfigFile(self):
        # 剩余表格的读取和转换操作。
        # Init_Sheet处理完毕，移除。
        self.sheet_names.remove("Init_Sheet")
        # print(self.sheet_names)
        self.ADST.ADST_Sheet_dict_Save_as_json_temp(self.target_file_path,self.sheet_names)

        self.ADST.ADST_Config_Classify_By_Device(self.sheet_names)
           
    def AD_Config_Start_Stage(self,InitConfig_path="AutoDevProFile/Temporary", Change_Name=False,InitConfig_Backup=False):

        InitConfig_path = os.path.join(InitConfig_path,"Temporary_InitConfig.json",)
        
        if self.ADOT.ADOT_Check_File(InitConfig_path):
            Init_list = self.ADOT.ADOT_Read_Data_From_json(InitConfig_path)
            Init_list_1 = self.ADOT.ADOT_InputList_Deletedict_value(Init_list,key="FTP_Server",value=1)
            # print(Init_list_1)
            Init_dict = self.ADOT.ADOT_InputList_ToDeviceIPDict(Init_list_1,key1="Device_Name",key2="Manage_IP")
            # print(Init_dict)
            test_result = []
            # 遍历字典，进行连通性测试
            for dev_name,test_ip in Init_dict.items():
                test_result_dict = {"Dev_Name":dev_name,"IP":test_ip}
                if self.ADTT.ADTT_test_ip_ping(test_ip):
                    test_result_dict["ping_reachable"] = True
                    ADCT = AutoDev_ConnectTools(Init_list)
                    
                    if ADCT.ADCT_Login(dev_name):
                        test_result_dict["SSH_reachable"] = True
                        print(f"✅ {test_ip} SSH可连接")
                        
                        if Change_Name:
                            print(f"启动改名模块：正在对{test_ip}进行改名操作。")
                            # init_command_list = self.AD_SystemConfig.ADSC_ChangeSystemName(dev_name) # 废弃写法，配置命令构成已经全部转到 AutoDev_Connector (接驳器)。
                            init_command_list = self.ADC.ADC_Function_Call(dev_name,mode="init")
                            # print(init_command_list)
                            ADCT.ADCT_Command_Issuance(init_command_list)
                            ADCT.ADCT_SaveConfig()
                            print(f"✅ 已改名为:{dev_name}。")

                        print(f"正在比对{test_ip}的设备名是否为：{dev_name}")
                        if ADCT.ADCT_GetDevName() == dev_name:
                            test_result_dict["Name_Comparison"] = "pass"
                        else:
                            test_result_dict["Name_Comparison"] = "fail"

                        if InitConfig_Backup:
                            print(f"启动配置存储模块：正在保存{dev_name}设备的配置文件。")
                            if ADCT.ADCT_SaveConfig():
                                Save_status,backup_file_path = ADCT.ADCT_BakCfg_Via_SFTP(process="init_backup",remote_path="AutoDevProFile/InitConfig_Backup")
                                test_result_dict["Backup_File"] = backup_file_path
                        ADCT.ADCTCloss()
    
                test_result.append(test_result_dict)
                  
            all_reachable_ping, unreachable_items_ping = self.ADOT.ADOT_Check_All_Value_Equal(dict_list=test_result,key="ping_reachable",target_value=True)
            
            if all_reachable_ping:
                # print("✅ 所有设备管理IP均可达。")
                all_reachable_SSH, unreachable_items_SSH = self.ADOT.ADOT_Check_All_Value_Equal(dict_list=test_result,key="SSH_reachable",target_value=True)
                
                if all_reachable_SSH:
                    # print("✅ 所有设备管理SSH均可达。")
                    all_Nam_Comparison, Name_UNComparison = self.ADOT.ADOT_Check_All_Value_Equal(dict_list=test_result,key="Name_Comparison",target_value="pass")
                    
                    if all_Nam_Comparison:
                        # print("✅ 所有设备名称均对应，可继续执行后续配置流程。")
                        print("✅ 已对所有设备进行检查。")
                        #测试结果写入 Temporary_DevicStatus.json
                        self.ADTT.ADTT_test_passresult_save(test_result)
                    else:
                        print("❌ 存在不对应的设备名称。")
                        unreachable_SSHs = [item["Dev_Name"] for item in Name_UNComparison]
                        print(f"不对应的设备名称: {unreachable_SSHs}")
                    
                else:
                    print("❌ 存在不可达的设备SSH。")
                    unreachable_SSHs = [item["IP"] for item in unreachable_items_SSH]
                    print(f"不可达的SSH列表: {unreachable_SSHs}")
                    
            else:
                print("❌ 存在不可达的设备IP，暂停配置流程。")
                unreachable_ips = [item["IP"] for item in unreachable_items_ping]
                print(f"不可达的IP列表: {unreachable_ips}")
                
        else:
            print("error")
            
    def AD_Config_Core(self):
        """
        该方法为AutoDev_Config的核心方法，用于将处理好的配置文件配置到设备上去。
        """
        Init_list,DeviceName_List = self.ADST.ADST_Get_InitConfig()
        self.sheet_names.remove("Init_Sheet")
        for DeviceName in DeviceName_List:
            print(f"🔧 正在配置设备: {DeviceName}")
        
            # ✅ 每个设备独立连接
            ADCT = AutoDev_ConnectTools(Init_list)
    
            try:
                Config_Command_Standardization_list_all = [{"command": "system-view ", "mode": "Quick", "time": ""}]
                for sheet_name in self.sheet_names:
                    print(f"  📄 处理表单: {sheet_name}")
                    Config_list = self.ADST.ADST_GetConfig(DeviceName, sheet_name)
                    Standardization_Config_list = self.ADST.ADST_Get_Standardization_Config_list(Config_list)
                    Config_Command_Standardization_list = self.ADC.ADC_Function_Call(Standardization_Config_list)
                    for Config_Command_Standardization in Config_Command_Standardization_list:
                        Config_Command_Standardization_list_all.append(Config_Command_Standardization)

                # 发送命令
                # print(Config_Command_Standardization_list_all)
                ADCT.ADCT_Login(DeviceName)  # 必须包含 connect + invoke_shell
                ADCT.ADCT_Command_Issuance(Config_Command_Standardization_list_all)

                # 保存配置
                ADCT.ADCT_SaveConfig()
                print(f"✅ 设备 {DeviceName} 配置完成并保存")

            except Exception as e:
                print(f"❌ 配置设备 {DeviceName} 时出错: {e}")
                raise  # 或 continue
            finally:
                ADCT.ADCTCloss()  # 安全关闭
          

    def AD_Config_End(self,Init_Sheet_dicts):
        pass


class AutoDev_OP:
    """
    AutoDev_OP类用于自动化运维，暂无开发意向(累了)，只画饼搭框架。
    
    """
    def __init__(self):
        pass

    def AD_OP_Get_Device_Status(self):
        """该方法用于获取更新设备状态"""
        pass

    def AD_OP_Get_Port_Status(self):
        """该方法用于获取接口状态"""
        pass
        
    def AD_OP_Get_Route_Status(self):
        """该方法用于获取路由状态"""
        pass

    
class AutoDev_CreateConfig:
    """
    AutoDev_CreateConfig类用于自动批量生成配置命令，根据实际业务需求开发。
    
    """
    def __init__(self,target_file_name="Auto_ConfigCommand_Create_Table_Template.xlsx"):

        # 构造参数
        self.target_file_name = target_file_name
        
        # 实例化基础工具类和数据表工具类
        self.ADOT = AutoDev_OtherTools()
        self.ADST = AutoDev_SheetTools()
        self.ADTT = AutoDev_TestTools()
        # self.AD_SystemConfig = AutoDev_SystemConfig()
        self.ADC = AutoDev_Connector()

        # 获取当前路径并构造配置表目录的绝对路径
        self.config_sheet_dir = self.ADOT.ADOT_GetAndCreat_contents("Config_Sheet")

        # 构造配置表绝对路径        
        self.target_file_path = os.path.join(self.config_sheet_dir, self.target_file_name)

        # 检查配置表是否存在，如果存在的话，导出配置表的表格名字。
        if self.ADOT.ADOT_Check_File(self.target_file_path):
            self.sheet_names = self.ADST.ADST_get_sheet_names(self.target_file_path)

        else:
            print("error")

    def AD_CreateConfig_File(self):
        pass

class AutoDev_Engineering_Test:
    """
    AutoDev_Engineering_Test类用于工程自动化测试
    """
    def __init__(self, target_file_dir: object = "none", target_file_name: object = "Automated_Test_Table_Template.xlsx") -> None:
        """
        工程测试类的初始化方法。
        :param target_file_name: 默认为在桌面的：Automated_Test_Table_Template.xlsx
        该文件的默认表格模版可以在项目的Config_Sheet目录下查找到。
        """
        # 构造参数
        self.target_file_name = target_file_name

        # 实例化基础工具类和数据表工具类
        self.ADOT = AutoDev_OtherTools()
        self.ADST = AutoDev_SheetTools()
        self.ADTT = AutoDev_TestTools()
        # self.AD_SystemConfig = AutoDev_SystemConfig()
        self.ADC = AutoDev_Connector()

        # 获取当前路径并构造配置表目录的绝对路径
        if target_file_dir == "normal":
            self.config_sheet_dir = self.ADOT.ADOT_GetAndCreat_contents("Config_Sheet")

        elif target_file_dir == "none":
            self.config_sheet_dir = os.path.join(self.ADOT.ADOT_Get_Desktop_Path())
            print(f"target_file_dir == none 已执行。")

        else:
            self.config_sheet_dir = target_file_dir

        # 构造配置表绝对路径
        self.target_file_path = os.path.join(self.config_sheet_dir, self.target_file_name)
        print(f"文件路径：{self.target_file_path}")

        # 检查配置表是否存在，如果存在的话，导出配置表的表格名字。
        if self.ADOT.ADOT_CheckEx_File_Or_Folder(self.target_file_path):
            self.sheet_names = self.ADST.ADST_get_sheet_names(self.target_file_path)
            print(self.sheet_names)

        else:
            print(f"error:测试表{self.target_file_name}不存在。")

        if "Test_Sheet" in self.sheet_names:
            Test_Sheet_dict_list = self.ADST.ADST_Export_Sheet_Standardization_dict(self.target_file_path,sheet_name="Test_Sheet")
            # print(Test_Sheet_dict)
        else:
            print(f"error:{self.target_file_path}该文件中没有Init_Sheet进行初始化")

        self.Test_Sheet_dict_list = Test_Sheet_dict_list


    def ADET_Test_Function(self):
        ADCT = AutoDev_ConnectTools(self.Test_Sheet_dict_list)
        self.Test_Result_dict_list = []
        print("🔧 正在并发执行 Ping 测试...")

        def test_icmp(test_dict):
            """仅执行 ICMP 测试"""
            ip = test_dict['Manage_IP']
            if self.ADTT.ADTT_test_ip_ping(ip):
                test_dict["ping_reachable"] = True
            else:
                test_dict["ping_reachable"] = False
            return test_dict

        # 无论设备数量多少，都使用多线程做 Ping（最多3个线程）
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_device = {
                executor.submit(test_icmp, test_dict): test_dict
                for test_dict in self.Test_Sheet_dict_list
            }

            for future in as_completed(future_to_device):
                try:
                    result = future.result()
                    self.Test_Result_dict_list.append(result)
                except Exception as exc:
                    device = future_to_device[future]
                    print(f"设备 {device['Manage_IP']} Ping 测试异常: {exc}")

        # 按原始顺序排序（重要）
        ip_to_result = {d['Manage_IP']: d for d in self.Test_Result_dict_list}
        self.Test_Result_dict_list = [
            ip_to_result[d['Manage_IP']]
            for d in self.Test_Sheet_dict_list
            if d['Manage_IP'] in ip_to_result
        ]

        print("🔐 正在串行执行 SSH 测试...")
        for test_dict in self.Test_Result_dict_list:
            ip = test_dict['Manage_IP']
            device_name = test_dict['Device_Name']

            # 只对 Ping 通的设备尝试 SSH
            try:
                if ADCT.ADCT_Login(device_name):
                    test_dict["SSH_reachable"] = True
                    ADCT.ADCTCloss()  # 立即关闭连接
                else:
                    test_dict["SSH_reachable"] = False
            except Exception as e:
                test_dict["SSH_reachable"] = False
                print(f"❌ {ip} 执行异常: {e}")

        # 调用结束处理
        self.ADET_Test_End()

    def ADET_Test_End(self):
        self.Test_Result_dict_list =[
            {k: v for k, v in device.items() if k not in ['Manager_Name', 'Manager_Password']}
            for device in self.Test_Sheet_dict_list
        ]
        # print(self.Test_Result_dict_list)
        self.ADOT.ADOT_Data_Tran_File(self.Test_Result_dict_list,file_name="test_result",save_dir=self.config_sheet_dir,file_format="json",include_date=True)











        
        