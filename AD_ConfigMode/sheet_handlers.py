


# 定义 sheet_name 到 (对象属性名, 方法名) 的映射
SHEET_HANDLER_MAP = {
    "Port_IP_Sheet(Router)": ("AD_SystemConfig", "adsc_port_ip"),
    "IP_Route_Static_Sheet": ("ADIR", "adir_static"),

}

# 可选：定义数据预处理策略（解决不同 sheet 数据格式差异）
SHEET_DATA_EXTRACTOR = {
    "Port_IP_Sheet(Router)": lambda param: param[1],          # 取第2个元素
    "IP_Route_Static_Sheet": lambda param: param[1:],         # 取从第2个开始的切片
    # 默认行为可设为 lambda param: param[1]
}