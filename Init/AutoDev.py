import time
from typing import final

from invoke.completion.complete import print_task_names

from Network_Automation_and_Operations.Init.AutoDevTools import *
from Network_Automation_and_Operations.Init.BaseTools import *
# from Network_Automation_and_Operations.AD_ConfigMode.AutoDevSystemConfig import *
from Network_Automation_and_Operations.AD_ConfigMode.AutoDevConnector import *
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class AutoDevConfig:
    """
    AutoDev_Config类用于自动化配置
    
    """
    def __init__(self,target_file_name="Automated_Configuration_Table_Template.xlsx"):

        # 构造参数
        self.target_file_name = target_file_name
        
        # 实例化基础工具类和数据表工具类
        self.ADOT = AutoDevOtherTools()
        self.ADST = AutoDevSheetTools()
        self.ADTT = AutoDevTestTools()
        # self.AD_SystemConfig = AutoDevSystemConfig()
        self.ADC = AutoDevConnector()

        # 获取当前路径并构造配置表目录的绝对路径
        self.config_sheet_dir = self.ADOT.adot_getandcreat_contents("Config_Sheet")

        # 构造配置表绝对路径        
        self.target_file_path = os.path.join(self.config_sheet_dir, self.target_file_name)

        # 检查配置表是否存在，如果存在的话，导出配置表的表格名字。
        if self.ADOT.adot_check_file(self.target_file_path):
            self.sheet_names = self.ADST.adst_get_sheet_names(self.target_file_path)

        else:
            print("error")

    def ad_config_getstartfile(self):
        if "Init_Sheet" in self.sheet_names:
            Init_Sheet_dict = self.ADST.adst_export_init_sheet_dict(self.target_file_path)
        else:
            print(f"error:{self.target_file_path}该文件中没有Init_Sheet进行初始化")

        # 针对初始化表格文件进行处理，并生成临时文件。
        self.ADST.adst_init_sheet_dict_save_as_json_temp(self.target_file_path)

    def ad_config_getconfigfile(self):
        # 剩余表格的读取和转换操作。
        # Init_Sheet处理完毕，移除。
        self.sheet_names.remove("Init_Sheet")
        # print(self.sheet_names)
        self.ADST.adst_sheet_dict_save_as_json_temp(self.target_file_path, self.sheet_names)

        self.ADST.adst_config_classify_by_device(self.sheet_names)
           
    def ad_config_start_stage(self,InitConfig_path="AutoDevProFile/Temporary", Change_Name=False,InitConfig_Backup=False):

        InitConfig_path = os.path.join(InitConfig_path,"Temporary_InitConfig.json",)
        
        if self.ADOT.adot_check_file(InitConfig_path):
            Init_list = self.ADOT.adot_read_data_from_json(InitConfig_path)
            Init_list_1 = self.ADOT.adot_inputList_deletedict_value(Init_list, key="FTP_Server", value=1)
            # print(Init_list_1)
            Init_dict = self.ADOT.adot_inputlist_todevice_ip_dict(Init_list_1, key1="Device_Name", key2="Manage_IP")
            # print(Init_dict)
            test_result = []
            # 遍历字典，进行连通性测试
            for dev_name,test_ip in Init_dict.items():
                test_result_dict = {"Dev_Name":dev_name,"IP":test_ip}
                if self.ADTT.adtt_test_ip_ping(test_ip):
                    test_result_dict["ping_reachable"] = True
                    ADCT = AutoDevConnectTools(Init_list)
                    
                    if ADCT.adct_login(dev_name):
                        test_result_dict["SSH_reachable"] = True
                        print(f"✅ {test_ip} SSH可连接")
                        
                        if Change_Name:
                            print(f"启动改名模块：正在对{test_ip}进行改名操作。")
                            # init_command_list = self.AD_SystemConfig.ADSC_ChangeSystemName(dev_name) # 废弃写法，配置命令构成已经全部转到 AutoDevConnector (接驳器)。
                            init_command_list = self.ADC.adc_function_call(dev_name, mode="init")
                            # print(init_command_list)
                            ADCT.adct_command_issuance(init_command_list)
                            ADCT.adct_saveconfig()
                            print(f"✅ 已改名为:{dev_name}。")

                        print(f"正在比对{test_ip}的设备名是否为：{dev_name}")
                        if ADCT.adct_getdevname() == dev_name:
                            test_result_dict["Name_Comparison"] = "pass"
                        else:
                            test_result_dict["Name_Comparison"] = "fail"

                        if InitConfig_Backup:
                            print(f"启动配置存储模块：正在保存{dev_name}设备的配置文件。")
                            if ADCT.adct_saveconfig():
                                Save_status,backup_file_path = ADCT.adct_bakcfg_via_sftp(process="init_backup",
                                                                                         remote_path="AutoDevProFile/InitConfig_Backup")
                                test_result_dict["Backup_File"] = backup_file_path
                        ADCT.adctcloss()
    
                test_result.append(test_result_dict)
                  
            all_reachable_ping, unreachable_items_ping = self.ADOT.adot_check_all_value_equal(dict_list=test_result,
                                                                                              key="ping_reachable",
                                                                                              target_value=True)
            
            if all_reachable_ping:
                # print("✅ 所有设备管理IP均可达。")
                all_reachable_SSH, unreachable_items_SSH = self.ADOT.adot_check_all_value_equal(dict_list=test_result,
                                                                                                key="SSH_reachable",
                                                                                                target_value=True)
                
                if all_reachable_SSH:
                    # print("✅ 所有设备管理SSH均可达。")
                    all_Nam_Comparison, Name_UNComparison = self.ADOT.adot_check_all_value_equal(dict_list=test_result,
                                                                                                 key="Name_Comparison",
                                                                                                 target_value="pass")
                    
                    if all_Nam_Comparison:
                        # print("✅ 所有设备名称均对应，可继续执行后续配置流程。")
                        print("✅ 已对所有设备进行检查。")
                        #测试结果写入 Temporary_DevicStatus.json
                        self.ADTT.adtt_test_passresult_save(test_result)
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
            
    def ad_config_core(self):
        """
        该方法为AutoDev_Config的核心方法，用于将处理好的配置文件配置到设备上去。
        """
        Init_list,DeviceName_List = self.ADST.adst_get_initConfig()
        self.sheet_names.remove("Init_Sheet")
        for DeviceName in DeviceName_List:
            print(f"🔧 正在配置设备: {DeviceName}")
        
            # ✅ 每个设备独立连接
            ADCT = AutoDevConnectTools(Init_list)
    
            try:
                Config_Command_Standardization_list_all = [{"command": "system-view ", "mode": "Quick", "time": ""}]
                for sheet_name in self.sheet_names:
                    print(f"  📄 处理表单: {sheet_name}")
                    Config_list = self.ADST.adst_getconfig(DeviceName, sheet_name)
                    Standardization_Config_list = self.ADST.adst_get_standardization_config_list(Config_list)
                    Config_Command_Standardization_list = self.ADC.adc_function_call(Standardization_Config_list)
                    for Config_Command_Standardization in Config_Command_Standardization_list:
                        Config_Command_Standardization_list_all.append(Config_Command_Standardization)

                # 发送命令
                # print(Config_Command_Standardization_list_all)
                ADCT.adct_login(DeviceName)  # 必须包含 connect + invoke_shell
                ADCT.adct_command_issuance(Config_Command_Standardization_list_all)

                # 保存配置
                ADCT.adct_saveconfig()
                print(f"✅ 设备 {DeviceName} 配置完成并保存")

            except Exception as e:
                print(f"❌ 配置设备 {DeviceName} 时出错: {e}")
                raise  # 或 continue
            finally:
                ADCT.adctcloss()  # 安全关闭
          

    def ad_config_end(self,Init_Sheet_dicts):
        pass


class AutoDevOP:
    """
    AutoDevOP类用于自动化运维，暂无开发意向(累了)，只画饼搭框架。
    
    """
    def __init__(self):
        pass

    def ad_op_get_device_status(self):
        """该方法用于获取更新设备状态"""
        pass

    def ad_op_get_port_status(self):
        """该方法用于获取接口状态"""
        pass
        
    def ad_op_get_route_status(self):
        """该方法用于获取路由状态"""
        pass


class AutoDevCreateConfig:
    """
    AutoDev_CreateConfig类用于自动批量生成配置命令，根据实际业务需求开发。
    
    """
    def __init__(self,target_file_name="Auto_ConfigCommand_Create_Table_Template.xlsx"):

        # 构造参数
        self.target_file_name = target_file_name
        
        # 实例化基础工具类和数据表工具类
        self.ADOT = AutoDevOtherTools()
        self.ADST = AutoDevSheetTools()
        self.ADTT = AutoDevTestTools()
        # self.AD_SystemConfig = AutoDevSystemConfig()
        self.ADC = AutoDevConnector()
        print(f"✅ 已完成基础参数和工具加载，开始构造表格路径和配置表检测。")

        # 获取当前路径并构造配置表目录的绝对路径
        self.config_sheet_dir = self.ADOT.adot_getandcreat_contents("Config_Sheet")

        # 构造配置表绝对路径        
        self.target_file_path = os.path.join(self.config_sheet_dir, self.target_file_name)
        print(f"✅ 已完成配置表绝对路径构造，路径为：{self.target_file_path},开始进行配置表检查。")

        # 检查配置表是否存在，如果存在的话，导出配置表的表格名字。
        if self.ADOT.adot_check_file(self.target_file_path):
            self.sheet_names_list = self.ADST.adst_get_sheet_names(self.target_file_path)
            print(f"✅ 已检查完毕，配置表存在，读取到配置表中的表格名字信息如下：{self.sheet_names_list}")

        else:
            print(f"⚠️ 已检查完毕，配置表不存在")

        # 请注意！！！！！init中的文件检测如若修改，则相关代码中关于打开文件的部分也需要修改，在代码内已经内置了目前的存放位置的路径。

    def ad_createconfig_file(self):
        # 使用已有工具方法将配置表中的数据导出并按设备分类好所需要的配置信息。
        # 将配置表中的内容导出转换为json文件，每个表格一个json文件。
        self.ADST.adst_sheet_dict_save_as_json_temp(self.target_file_path, self.sheet_names_list,save_dir="AutoDevProFile/Temporary/CreateConfigModel/")
        # 将json文件中的信息按设备进行分类，每个设备构造一个json文件，并输出设备名称列表。
        device_list = self.ADST.adst_config_classify_by_device(self.sheet_names_list,mode="AutoDevCreateConfig")
        # print(device_list)

        # 生成各个设备独立的配置单
        for devicename in device_list:
            print(f"🔧 正在生成{devicename}的配置")
            config_command_standardization_list_all = ["system-view "]
            # print(self.sheet_names_list)
            for sheet_name in self.sheet_names_list:
                print(f"  📄 正在处理表单: {sheet_name}")
                config_list = self.ADST.adst_getconfig(devicename, sheet_name,file_path="/AutoDevProFile/Temporary/CreateConfigModel/Temporary_")
                # print(config_list)
                if config_list:
                    standardization_config_list = self.ADST.adst_get_standardization_config_list(config_list)
                    # print(standardization_config_list)
                    config_command_standardization_list = self.ADC.adc_function_call(standardization_config_list,mode="create_config_command",sysname=devicename)
                    # print(config_command_standardization_list)
                    for config_command_standardization in config_command_standardization_list:
                        config_command_standardization_list_all.append(config_command_standardization)
                    # print(config_command_standardization_list_all)
                else:
                    print(f"{sheet_name}为空，跳过。")
            # print(config_command_standardization_list_all)
            print(f"正在保存{devicename}配置信息......")
        #     time.sleep(0.5)
        #     final_file_save_path = self.ADOT.adot_get_desktop_path() + "/createconfig"
        #     self.ADOT.adot_data_tran_file(config_command_standardization_list_all,file_name=devicename,save_dir=final_file_save_path,include_date=True)
        #     time.sleep(0.5)
        # print(f"已完成所有配置文件生成。")



class AutoDevEngineeringTest:
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
        self.ADOT = AutoDevOtherTools()
        self.ADST = AutoDevSheetTools()
        self.ADTT = AutoDevTestTools()
        # self.AD_SystemConfig = AutoDevSystemConfig()
        self.ADC = AutoDevConnector()

        # 获取当前路径并构造配置表目录的绝对路径
        if target_file_dir == "normal":
            self.config_sheet_dir = self.ADOT.adot_getandcreat_contents("Config_Sheet")

        elif target_file_dir == "none":
            self.config_sheet_dir = os.path.join(self.ADOT.adot_get_desktop_path())
            print(f"target_file_dir == none 已执行。")

        else:
            self.config_sheet_dir = target_file_dir

        # 构造配置表绝对路径
        self.target_file_path = os.path.join(self.config_sheet_dir, self.target_file_name)
        print(f"文件路径：{self.target_file_path}")

        # 检查配置表是否存在，如果存在的话，导出配置表的表格名字。
        if self.ADOT.adot_checkex_file_or_folder(self.target_file_path):
            self.sheet_names = self.ADST.adst_get_sheet_names(self.target_file_path)
            print(self.sheet_names)

        else:
            print(f"error:测试表{self.target_file_name}不存在。")

        if "Test_Sheet" in self.sheet_names:
            Test_Sheet_dict_list = self.ADST.adst_export_sheet_standardization_dict(self.target_file_path,
                                                                                    sheet_name="Test_Sheet")
            # print(Test_Sheet_dict)
        else:
            print(f"error:{self.target_file_path}该文件中没有Init_Sheet进行初始化")

        self.Test_Sheet_dict_list = Test_Sheet_dict_list


    def adet_test_function(self):
        ADCT = AutoDevConnectTools(self.Test_Sheet_dict_list)
        self.Test_Result_dict_list = []
        print("🔧 正在并发执行 Ping 测试...")

        def test_icmp(test_dict):
            """仅执行 ICMP 测试"""
            ip = test_dict['Manage_IP']
            if self.ADTT.adtt_test_ip_ping(ip):
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
                if ADCT.adct_login(device_name):
                    test_dict["SSH_reachable"] = True
                    ADCT.adctcloss()  # 立即关闭连接
                else:
                    test_dict["SSH_reachable"] = False
            except Exception as e:
                test_dict["SSH_reachable"] = False
                print(f"❌ {ip} 执行异常: {e}")

        # 调用结束处理
        self.adet_test_end()

    def adet_test_end(self):
        self.Test_Result_dict_list =[
            {k: v for k, v in device.items() if k not in ['Manager_Name', 'Manager_Password']}
            for device in self.Test_Sheet_dict_list
        ]
        # print(self.Test_Result_dict_list)
        self.ADOT.adot_data_tran_file(self.Test_Result_dict_list, file_name="test_result",
                                      save_dir=self.config_sheet_dir, file_format="json", include_date=True)











        
        