# 文件：test_client.py
import requests
import json

# 1. 定义你的 Agent 服务地址（和刚才浏览器里访问的是同一个）
URL = "http://127.0.0.1:8000/diagnose"

def ask_agent(question: str):
    """
    向 Agent 发送问题，并打印返回结果
    """
    # 准备要发送的数据（JSON 格式）
    payload = {
        "question": question
    }
    
    print(f"🤔 正在询问: {question}")
    print("-" * 40)
    
    try:
        # 发送 POST 请求
        response = requests.post(URL, json=payload)
        
        # 检查 HTTP 状态码
        if response.status_code == 200:
            # 解析返回的 JSON 数据
            result = response.json()
            # 提取 answer 字段并打印
            print("✅ Agent 回答:\n")
            print(result["answer"])
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器！请确认 api_server.py 是否正在运行。")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")

# ============================================================================
# 程序入口
# ============================================================================
if __name__ == "__main__":
    # 你可以在这里直接写死一个问题，也可以让它交互式输入
    
    # 方式 1：直接测试（适合快速验证）
    # ask_agent("故障E101怎么处理")
    
    # 方式 2：交互式输入（可以连续问问题）
    while True:
        user_input = input("\n请输入您的设备问题（输入 'q' 退出）: ")
        if user_input.lower() == 'q':
            print("👋 再见！")
            break
        if user_input.strip():
            ask_agent(user_input)
        else:
            print("⚠️ 问题不能为空，请重新输入。")