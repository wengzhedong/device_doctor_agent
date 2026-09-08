# 文件：2_offline/build_vector_index.py
import sys
import os
# 将项目根目录（device_doctor_agent）添加到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from data_prepare import load_and_split_documents
from config.settings import Config  # 导入配置文件

def build_index():
    print("\n=== 开始加载文档 ===")
    parent_docs, child_docs = load_and_split_documents()

    print("\n=== 初始化嵌入模型 ===")
    embeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},   
        encode_kwargs={'normalize_embeddings': True}
    )

    print("\n=== 开始向量化入库 ===")
    vectorstore = Chroma.from_documents(
        documents=child_docs,
        embedding=embeddings,
        persist_directory=Config.CHROMA_PERSIST_DIR
    )
    vectorstore.persist()
    print(f"   - 父块: {len(parent_docs)} 个")
    print(f"   - 子块: {len(child_docs)} 个（已入库）")
    print(f"✅ 向量库构建完成！存储路径：{Config.CHROMA_PERSIST_DIR}")

if __name__ == "__main__":
    build_index()