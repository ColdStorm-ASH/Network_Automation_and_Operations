import subprocess
from sys import stderr

test_ips = ["192.168.56.3","192.168.56.4","192.168.56.5"]

print(f"开始网络连通性测试....")

for ip in test_ips:
    command = ['ping', ip]
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            print(f"{ip}可达")

        else:
            print(f"{ip}不可达")
            if result.stderr.strip():
                print("错误信息：",result.stderr.strip())

    except Exception as e:
        print(f"执行ping{ip}时出错：{e}")

print("网络测试完成")