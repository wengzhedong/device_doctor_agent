import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import Config

def load_and_split_documents():
    """加载PDF并执行父子分段"""
    print("正在加载PDF...")
    loader = PyPDFLoader(f"{Config.DATA_DIR}/cnc_fault_manual.pdf")
    docs = loader.load()
    print(f"加载完成，共 {len(docs)} 页")

    # 父块切分：从配置文件读取参数
    print("正在切分父块...")
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.PARENT_CHUNK_SIZE,
        chunk_overlap=Config.PARENT_CHUNK_OVERLAP
    )
    parent_docs = parent_splitter.split_documents(docs)
    print(f"父块数量: {len(parent_docs)}")

    # 子块切分：从配置文件读取参数
    print("正在切分子块...")
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHILD_CHUNK_SIZE,
        chunk_overlap=Config.CHILD_CHUNK_OVERLAP
    )

    child_docs = []
    for idx, parent in enumerate(parent_docs):
        parent_content = parent.page_content
        chunks = child_splitter.split_documents([parent])
        for chunk in chunks:
            chunk.metadata["parent_content"] = parent_content
            chunk.metadata["parent_id"] = idx
            child_docs.append(chunk)

    print(f"子块数量: {len(child_docs)}")
    return parent_docs, child_docs