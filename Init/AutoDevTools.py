import paramiko
import time
import subprocess
import re
from Network_Automation_and_Operations.Init.BaseTools import AutoDevOtherTools

"""
    该py文件存放了AutoDevTestTools类和AutoDevConnectTools类，实例化对象时一般缩写为ADTT和ADCT。


"""

""" ↓↓ 这是方法分类注释 ↓↓ """
""" 上下注释中间内容为某个分类的方法 """
""" ↑↑ 这是方法分类注释 ↑↑ """

"""----- AutoDevTestTools类头部 -----"""
class AutoDevTestTools:
    def __init__(self,count=5, timeout=5):
        self.count = count
        self.timeout = timeout
        self.ADOT = AutoDevOtherTools()

    def adtt_test_ip_ping(self,ip):
        if self.count != 5 or self.timeout != 5:
            ADTTCommand = ['ping', '-c', str(self.count), '-W', str(self.timeout), ip]

        else:
            ADTTCommand = ['ping', ip]

        try:
            result = subprocess.run(
                ADTTCommand,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode == 0:
                print(f"✅ {ip} 可达")
                return True
            else:
                print(f"❌ {ip} 不可达")
                if result.stderr.strip():
                    print("错误信息:", result.stderr.strip())
                return False

        except Exception as e:
            print(f"⚠️ 执行 ping {self.ip} 时出错: {e}")
            return False

    def adtt_test_passresult_save(self,test_result):
        test_result_dict = self.ADOT.adot_createdict_passresult()
        test_result.append(test_result_dict)
        self.ADOT.adot_data_tran_file(test_result, file_name="DevicStatus", save_dir="AutoDevProFile/Temporary/",file_format="json")
        

"""----- AutoDevTestTools类结尾 -----"""

"""----- AutoDevConnectTools类头部 -----"""
class AutoDevConnectTools:
    def __init__(self, Init_list: object) -> None:
        # 注释留白
        self.Init_list = Init_list
        # print(f"实例化ADCT：{self.Init_list}")

        # 实例化对象
        self.ADOT = AutoDevOtherTools()
        
        self.SFTP_IP = "192.168.56.2"
        self.SFTP_Uname = "py-auto-dev"
        self.SFTP_pwd = "H3C-py"

    def adct_login(self,Connect_Dev):
        
        matched_devices = self.ADOT.adot_inputlist_finddictbyvalue(self.Init_list, key="Device_Name", value=Connect_Dev)
        # print(matched_devices)

        # 判断是否恰好找到一个匹配项
        if not matched_devices:
            raise ValueError(f"未找到设备名称为 '{Connect_Dev}' 的设备配置。")
        elif len(matched_devices) > 1:
            raise ValueError(f"找到多个设备名称为 '{Connect_Dev}' 的配置，设备名应唯一。请检查配置列表。")

        # 此时 matched_devices 只有一个元素
        device_config = matched_devices[0]

        # 从配置中提取连接信息
        self.ip = device_config.get("Manage_IP")
        self.username = device_config.get("Manager_Name")
        self.password = device_config.get("Manager_Password")

        if not all([self.ip, self.username, self.password]):
            missing = [k for k, v in {"Manage_IP": self.ip, "Manager_Name": self.username, "Manager_Password": self.password}.items() if not v]
            raise ValueError(f"设备配置缺少必要字段: {missing}")

        """创建SSH连接，并激活shell"""
        try:
            self.ssh_client = paramiko.SSHClient()  # 实例化SSHClient
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动添加策略，保存服务器主机名和密钥信息
            self.ssh_client.connect(hostname=self.ip, username=self.username, password=self.password)  # 连接SSH服务端，以用户名和密码进行认证

            self.command = self.ssh_client.invoke_shell()  # 在客户端激活shell 
            time.sleep(1)  # 等待 shell 启动
            ADTLogin_Result = self.ip + " SSH连接已激活"
            print(ADTLogin_Result)
            return True
            
        except Exception as e:
            print(f"SSH连接失败 [{self.ip}]: {str(e)}")
            return False

    def adctcommand_quicky(self,ADCommand="",sleep_time=1):
        """键入命令，Quicky没有输出，默认休息时间为：1"""
        self.command.send(ADCommand + "\n")  # 输入dis version命令
        print(f"执行Quicky中，命令为：{ADCommand}")
        time.sleep(sleep_time)  # 线程推迟1S运行 = 休眠1S'

    def adctcommand_recv(self,ADCommand="",sleep_time=2):
        """键入命令，Recv会return输出，默认休息时间为：2"""
        self.command.send(ADCommand + "\n")  # 输入命令
        print(f"执行Recv中，命令为：{ADCommand}")
        time.sleep(sleep_time)  # 线程推迟1S运行 = 休眠1S'
        ADTCommand_Rec_output = self.command.recv(65535).decode("ascii")  # 接收的最大字节数
        # print(ADTCommand_Rec_output)
        return ADTCommand_Rec_output

    def adctcloss(self):
        self.command.send("\x1a")
        time.sleep(1)
        self.ssh_client.close()

    def adct_getdevname(self):
        """获取设备名称（<DeviceName>）"""
        self.command.send("\x1a\n")  # 返回用户视图
        time.sleep(1)
        output = self.command.recv(65535).decode("ascii")
        match = re.findall(r'<(.*?)>', output, re.S)
        if match:
            return match[0].strip()
        else:
            raise Exception("❌ 无法获取设备名称")

    def adct_create_datename(self,process="backup"):
        device_name = self.adct_getdevname()
        ADOT = AutoDevOtherTools()
        if process == "backup":
            new_file_Datename = ADOT.adot_getdate_filename(device_name,"startup.cfg")
        elif process == "init_backup":
            new_file_Datename = ADOT.adot_getdate_filename(device_name,"init_config.cfg")
        else:
            new_file_Datename = ADOT.adot_getdate_filename(device_name,process+".cfg")
            
        return new_file_Datename

    def adct_detect_output(self, output,detect_type="InitConfig",dev_name=""):
        """判断输出内容用于交互处理"""
        ADOT = AutoDevOtherTools()
        last_line = ADOT.adot_get_last_line(output)  # 只看最后一行
        # print(f"最后一行: {repr(last_line)}")  # 调试用，能看到换行符等

        if detect_type == "SFTPLogin":
            if ("The server is not authenticated. Continue? [Y/N]:" in last_line or 
                "Do you want to save the server public key? [Y/N]:" in last_line or 
                "Please type 'Y' or 'N':" in last_line):
                # print("SFTPLogin 交互验证结果：1")
                return 1
            elif f"{self.SFTP_Uname}@{self.SFTP_IP}'s password:" in last_line:
                # print("SFTPLogin 交互验证结果：0")
                return 0
            else:
                # print("SFTPLogin 交互验证结果：None")
                return None
                
        elif detect_type == "SaveConfig":
            if ("flash:/startup.cfg exists, overwrite? [Y/N]:" in last_line or
                "The current configuration will be written to the device. Are you sure? [Y/N]:" in last_line):
                # print("SaveConfig 交互验证结果：1")
                return 1
            elif ("guration is saved to device successfully." in last_line or 
                  "Configuration is saved to device successfully." in last_line):
                # print("SaveConfig 交互验证结果：0")
                return 0
            elif "(To leave the existing filename unchanged, press the enter key):" in last_line:
                # print("SaveConfig 交互验证结果：2")
                return 2
            else:
                # print("SaveConfig 交互验证结果：None")
                return last_line

        elif detect_type == "InitConfig":
            right_output = f"<{dev_name}>"
            if right_output in last_line:
                return 0
            else:
                return 1

    def adct_saveconfig(self):
        self.adctcommand_quicky("\x1a")
        SaveConfig_output = self.adctcommand_recv("save")
        while True:
            tag = self.adct_detect_output(SaveConfig_output, detect_type="SaveConfig")
            if tag == 0:
                break
            elif tag == 1:
                SaveConfig_output = self.adctcommand_recv("Y")
            elif tag == 2:
                SaveConfig_output = self.adctcommand_recv(sleep_time=1)
            else:
                # print(tag)
                if self.adct_getdevname() == tag[1:-1]:
                    break
                else:
                    SaveConfig_output = self.adctcommand_recv()

        # self.ADCTCommand_Quicky()
        return True

    def adct_initconfig(self,dev_name):
        InitConfig_output = self.adctcommand_recv("\x1a")
        print(InitConfig_output)

        return True
        

    def adct_bakcfg_via_sftp(self,process="backup",remote_path="AutoDevProFile/Temporary"):
        """执行 SFTP 备份 startup.cfg 到远程服务器"""
        try:
            new_file_name = self.adct_create_datename(process)
            # remote_path = f"/home/py-auto-dev/AutoDevPro/Device_Config_Backup/{new_file_name}"
            backup_file_path = F"AutoDevPro/{remote_path}/{new_file_name}"
            # print(backup_file_path)

            # print(f"🔧 开始 SFTP 备份，目标文件名: {new_file_name}")
            print(f"🔧 开始 SFTP 备份.......")

            # 进入 SFTP
            self.adctcommand_quicky(f"sftp {self.SFTP_IP}")
            FTPLogin_output = self.adctcommand_recv(self.SFTP_Uname)
            # print(FTPLogin_output)

            # 处理认证交互
            while True:
                tag = self.adct_detect_output(FTPLogin_output, detect_type="SFTPLogin")
                if tag == 0:
                    break
                elif tag == 1:
                    FTPLogin_output = self.adctcommand_recv("Y")

                else:
                    FTPLogin_output = self.adctcommand_recv()

            # 输入密码
            PWD_Output = self.adctcommand_recv(self.SFTP_pwd)

            if "sftp>" not in PWD_Output:
                print("❌ SFTP 登录失败")
                return False

            print("✅ SFTP 登录成功，开始上传...")

            # 执行上传
            SFTP_result_output = self.adctcommand_recv(f"put startup.cfg {backup_file_path}", sleep_time=3)
            # print(SFTP_result_output)

            if "100%" in SFTP_result_output or "Transfer complete" in SFTP_result_output:
                print(f"✅ 配置文件已成功上传至 {backup_file_path}")
            else:
                print("❌ 文件上传失败")

            # 退出 SFTP
            self.adctcommand_quicky("quit")
            return True,backup_file_path

        except Exception as e:
            print(f"❌ SFTP 备份过程中发生异常: {e}")
            return False
        
    def adct_command_issuance(self, command_list):
        if not self.command or self.command.closed:
            raise Exception("❌ SSH channel 未连接或已关闭，无法发送命令")
            
        for command_dict in command_list:
            if not isinstance(command_dict, dict):
                print(f"⚠️ 跳过非字典命令: {command_dict}")
                continue
            print(command_dict)
            cmd = command_dict.get('command')
            mode = command_dict.get('mode')
            time_str = command_dict.get('time', '')  # 默认为空字符串

            # 提取 sleep_time，如果 time 是有效数字则转换，否则为 None
            try:
                sleep_time = float(time_str) if time_str and time_str.strip() != "" else None
            except (ValueError, TypeError):
                sleep_time = None

            # 根据 mode 调用对应方法
            if mode == "Quick":
                if sleep_time is not None:
                    self.adctcommand_quicky(cmd, sleep_time)
                else:
                    self.adctcommand_quicky(cmd)
            elif mode == "Recv":
                if sleep_time is not None:
                    self.adctcommand_recv(cmd, sleep_time)
                else:
                    self.adctcommand_recv(cmd)
            else:
                # 可选：处理未知 mode
                print(f"Unknown mode: {mode}")

"""----- AutoDevConnectTools类结尾 -----"""







    