import sys
import os
sys.path.insert(0, os.getcwd())

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from config.settings import Config

def test_retrieval():
    # 1. 初始化嵌入模型（必须和建库时一致）
    embeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # 2. 加载向量库
    vectorstore = Chroma(
        persist_directory=Config.CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )
    
    # 3. 检索测试
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
    results = retriever.invoke("故障E101")
    
    # 4. 打印结果
    print("\n=== 检索测试结果 ===")
    for i, doc in enumerate(results, 1):
        print(f"\n--- 结果 {i} ---")
        print(f"子块内容（前50字）: {doc.page_content[:50]}...")
        print(f"父块内容（前50字）: {doc.metadata.get('parent_content', '无')[:50]}...")
        print(f"父块ID: {doc.metadata.get('parent_id', '无')}")

if __name__ == "__main__":
    test_retrieval()