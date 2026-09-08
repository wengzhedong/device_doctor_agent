import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.tools import tool
import random #模拟用

@tool
def query_device_status(device_id: str) -> str:
    """
    查询指定设备的实时运行状态，包括温度、转速、振动值等。
    当用户询问设备实时状态时，应调用此工具。
    """
    temp = random.randint(70, 100)
    rpm = random.randint(800, 2500)
    vibration = round(random.uniform(0.5, 3.0), 1)
    
    return f"""设备ID: {device_id}
主轴温度: {temp}℃
主轴转速: {rpm} RPM
振动值: {vibration} mm/s
状态: {'⚠️ 注意' if temp > 90 else '✅ 正常运行'}"""