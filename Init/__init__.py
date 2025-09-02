"""
Init库—
       |— AutoDev.py文件 —
         |— AutoDev_Config类 —
           |该类用于实现自动化配置
           ——————————————————————
           |— init —
             |可传参数：target_file_name —— 用于指定标准化模版表格文件名，默认值是：Automated_Configuration_Table_Template.xlsx
             |初始化方法包含配置表模版读取
             |实例化基础工具类和数据表工具类
             |导出配置表的表格名字（列表）
             ——————————————————————
           |— AD_Config_GetStartFile —
             |获取Init_Sheet表中的信息
             |导出表格信息（字典）
             |将字典转为json文件格式保存至./AutoDevProFile/Temporary/Temporary_InitConfig.json
             ——————————————————————
           |— AD_Config_GetConfigFile —
             |获取其他表格信息
             |导出表格信息（字典），并转为临时json文件保存至目录./AutoDevProFile/Temporary/下
             |将./AutoDevProFile/Temporary/目录下的临时表格文件按设备分类配置并为每个设备生成单独的配置信息json文件。
             ——————————————————————
           |— AD_Config_Start_Stage —
             |
             |
             |
             ——————————————————————
           |— AD_Config_Core —
           
           |— AD_Config_End —
           
         |— AutoDev_OP类 —
           |— init —
             |
             ——————————————
         
         |— AutoDev_CreateConfig类 —
           |— init —
             |
             ——————————————

         |— AutoDev_Engineering_Test类 —
           |— init —
             |
             ——————————————


       |—
       |—
  
"""