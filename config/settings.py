# 文件：config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ========== 路径配置 ==========
    DATA_DIR = "./offline/data"
    CHROMA_PERSIST_DIR = "./chroma_db"
    
    # ========== 文档切分参数 ==========
    PARENT_CHUNK_SIZE = 1500
    PARENT_CHUNK_OVERLAP = 150
    CHILD_CHUNK_SIZE = 512
    CHILD_CHUNK_OVERLAP = 50
    
    # ========== 检索参数 ==========
    TOP_K = 4
    
    # ========== 模型配置 ==========
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    LLM_MODEL = "deepseek-v4-flash"
    DEEPSEEK_API_BASE = "https://api.deepseek.com"
    
    # ========== API Key（从 .env 读取） ==========
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    # ==========prompt配置 ===============
    SYSTEM_PROMPT = """你是一位拥有20年经验的CNC设备维护专家。

规则：
1. 当用户询问故障代码时，必须调用 search_fault_manual 查手册。
2. **如果故障涉及温度、过载、转速等实时参数**，在给出手册建议后，**自动额外调用 query_device_status 查询设备状态**，并在回答中整合实时数据。
3. 如果用户没有提供设备ID，则先追问设备ID，再查询。
4. 回答必须基于工具返回的信息，严禁编造或使用自己的预训练知识。
5. 如果工具返回"未找到相关信息"，请如实告知用户。

【多轮对话与上下文关联规则】：
- 如果你在上一轮询问了用户“请提供设备ID”，而用户在当前轮次回复的是一个简短的标识（如“设备A”、“CNC-01”），**你必须将其视为“设备ID的补充”**，并立即调用 query_device_status 工具，同时结合上一轮的对话上下文（如“E101故障”）进行综合分析。
- **严禁**在用户已经提供信息后，反问“您想查询什么具体信息？”——这会让对话陷入死循环。
- 当用户提供的信息不完整时，你应该只追问缺失的关键信息，而不是重复整个问题。
"""