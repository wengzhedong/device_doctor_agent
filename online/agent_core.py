# 文件：online/agent_core.py
import sys
import os
# 将项目根目录添加到 Python 路径，确保能找到 config 和 tools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI

# 导入工具
from tools.rag_tool import search_fault_manual
from tools.device_api_tool import query_device_status
from config.settings import Config

# ============================================================================
# 1. 定义 Agent 的“记忆聊天窗口”（State）
# ============================================================================
class AgentState(TypedDict):
    # messages 是一个列表，记录所有对话和思考过程
    # add_messages 表示每次有新消息就追加到列表末尾
    messages: Annotated[Sequence[BaseMessage], add_messages]

# ============================================================================
# 2. 准备工具列表
# ============================================================================
tools = [search_fault_manual, query_device_status]

# ============================================================================
# 3. 初始化大模型（DeepSeek）并绑定工具
# ============================================================================
model = ChatOpenAI(
    model=Config.LLM_MODEL,                 # 从配置文件读取，如 deepseek-v4-flash
    openai_api_key=Config.DEEPSEEK_API_KEY,
    openai_api_base=Config.DEEPSEEK_API_BASE,
    temperature=0                           # 0 表示最确定性输出，减少随机发挥
)
# bind_tools 告诉大模型："你可以调用这些工具"
model_with_tools = model.bind_tools(tools)



# ============================================================================
# 4. 定义节点函数（Node Functions）
# ============================================================================

# 4.1 Agent 节点（大脑）：负责"思考"和"决策"
def call_model(state: AgentState):
    """
    这个节点会：
    1. 把系统提示词和用户消息组装起来
    2. 发给大模型（DeepSeek）
    3. 大模型可能直接回答，也可能返回"我要调用工具"
    """
    messages = state["messages"]
    # 把系统提示词插入到消息列表的最前面
    full_messages = [SystemMessage(content=Config.SYSTEM_PROMPT)] + messages
    # 调用大模型（它已经知道可以用哪些工具了）
    response = model_with_tools.invoke(full_messages)
    # 把大模型的"思考结果"写回黑板（State）
    return {"messages": [response]}

# 4.2 工具节点（手脚）：负责"执行动作"
# ToolNode 是 LangGraph 预置的节点，它会自动识别大模型要求调用的工具并执行
tool_node = ToolNode(tools)

# ============================================================================
# 5. 定义路由函数（Router）：决定"下一步去哪"
# ============================================================================
def router(state: AgentState):
    """
    这个函数检查大模型刚才的"决定"：
    - 如果大模型说"我要调用工具"，就去 'tools' 节点执行
    - 如果大模型没说调用工具，就结束流程 (END)
    """
    # 获取最后一条消息（就是大模型刚刚返回的那条）
    last_message = state["messages"][-1]
    
    # 检查这条消息里有没有"要求调用工具"的标记
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        # 有工具调用 → 去执行
        return "tools"
    else:
        # 没有工具调用 → 直接结束，输出答案
        return END

# ============================================================================
# 6. 构建图（Graph）—— 把上面的零件全部组装起来
# ============================================================================

# 创建状态图，以 AgentState 作为"黑板"
builder = StateGraph(AgentState)

# 添加节点
builder.add_node("agent", call_model)   # 大脑节点
builder.add_node("tools", tool_node)    # 手脚节点

# 设置入口：用户进来先进入 "agent" 节点（先让大脑思考）
builder.set_entry_point("agent")

# 添加条件边：从 agent 节点出来后，由 router 函数决定下一步
# 如果 router 返回 "tools"，就去 tools 节点
# 如果 router 返回 END，就结束
builder.add_conditional_edges("agent", router, {
    "tools": "tools",
    END: END
})

# 添加普通边：执行完 tools（手脚）后，必须回到 agent（大脑）重新思考
# 这是 Agent 能够"循环"的关键！
builder.add_edge("tools", "agent")

# 编译：把图变成可执行的程序
agent = builder.compile()

# 打印成功信息
print("✅ Agent 编译成功！")