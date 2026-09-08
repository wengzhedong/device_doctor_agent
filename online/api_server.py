# 文件：online/api_server.py
import sys
import os
# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from online.agent_core import agent

# ============================================================================
# 1. 创建 FastAPI 应用实例
# ============================================================================
app = FastAPI(
    title="设备故障诊断 Agent",
    description="基于 LangGraph + DeepSeek 构建的智能制造助手",
    version="1.0.0"
)

# ============================================================================
# 2. 定义请求和响应的数据模型（Pydantic）
# ============================================================================
class QueryRequest(BaseModel):
    """用户请求的格式"""
    question: str                # 用户的问题，如 "故障E101怎么处理？"
    # 可以扩展其他字段，比如 user_id, session_id 等

class QueryResponse(BaseModel):
    """服务响应的格式"""
    answer: str                  # Agent 的回答
    status: str = "success"      # 状态标识，默认 success

# ============================================================================
# 3. 核心接口：诊断接口（POST /diagnose）
# ============================================================================
@app.post("/diagnose", response_model=QueryResponse)
async def diagnose(request: QueryRequest):
    """
    接收用户问题，调用 Agent 生成诊断建议。
    """
    try:
        # 3.1 将用户问题包装成 HumanMessage，传给 Agent
        result = agent.invoke({
            "messages": [HumanMessage(content=request.question)]
        })
        
        # 3.2 从 Agent 的返回结果中提取最终答案
        # Agent 的黑板（State）里存了一整串消息历史
        # 我们需要从后往前找，找到最后一条 AI 的回答
        for msg in reversed(result["messages"]):
            if hasattr(msg, "content") and msg.content:
                return QueryResponse(answer=msg.content)
        
        # 如果循环结束都没找到有效的回答，返回一个默认消息
        return QueryResponse(answer="未能生成有效答案。", status="error")
    
    except Exception as e:
        # 如果发生异常，返回 500 错误和具体异常信息
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 4. 健康检查接口（GET /health）
# ============================================================================
@app.get("/health")
async def health_check():
    """
    用于检查服务是否正常运行。
    """
    return {"status": "running", "message": "设备故障诊断 Agent 服务正常"}

# ============================================================================
# 5. 启动入口
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,                      # FastAPI 应用实例
        host="0.0.0.0",           # 监听所有网络接口（允许外部访问）
        port=8000,                # 监听端口
        log_level="info"          # 日志级别
    )