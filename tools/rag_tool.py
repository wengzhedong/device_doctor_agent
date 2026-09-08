import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.tools import tool
from config.settings import Config

@tool
def search_fault_manual(query: str) -> str:
    """
    从设备故障手册中检索相关故障信息。
    当用户询问具体故障代码（如E101、E205）或故障现象时，应调用此工具。
    """
    embeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    vectorstore = Chroma(
        persist_directory=Config.CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": Config.TOP_K})
    docs = retriever.invoke(query)
    
    if not docs:
        return "手册中未找到相关信息。"
    
    full_contexts = []
    for doc in docs:
        parent_content = doc.metadata.get("parent_content")
        if parent_content:
            full_contexts.append(parent_content)
        else:
            full_contexts.append(doc.page_content)
    
    unique_contexts = list(dict.fromkeys(full_contexts))
    return "\n\n---\n\n".join(unique_contexts)