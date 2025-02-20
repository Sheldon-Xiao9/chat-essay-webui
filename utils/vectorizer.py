import os
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from .model_loader import ModelLoader
from .file_processor import FileProcessor

class Vectorizer:
    """向量化处理工具类"""
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.file_processor = FileProcessor()
        self.embedding_model = self.model_loader.load_embedding_model()
        
    def create_vector_store(self, texts: List[str], store_name: str) -> FAISS:
        """
        创建向量存储
        """
        if not texts:
            raise ValueError("No texts provided for vectorization")
            
        try:
            # 创建向量存储
            vector_store = FAISS.from_texts(
                texts,
                self.embedding_model
            )
            
            # 确保vector_store目录存在
            os.makedirs("database/vector_store", exist_ok=True)
            
            # 保存向量存储
            vector_store.save_local(f"database/vector_store/{store_name}")
            
            return vector_store
            
        except Exception as e:
            raise Exception(f"Error creating vector store: {str(e)}")
    
    def load_vector_store(self, store_name: str) -> Optional[FAISS]:
        """
        加载向量存储
        """
        store_path = f"database/vector_store/{store_name}"
        
        if not os.path.exists(store_path):
            return None
            
        try:
            vector_store = FAISS.load_local(
                store_path,
                self.embedding_model
            )
            return vector_store
            
        except Exception as e:
            raise Exception(f"Error loading vector store: {str(e)}")
    
    def process_file(self, file_path: str, store_name: str) -> FAISS:
        """
        处理文件并创建向量存储
        """
        # 加载文档
        texts = self.file_processor.load_document(file_path)
        
        # 文本分块
        chunks = []
        for text in texts:
            chunks.extend(self.file_processor.split_text(text))
        
        # 创建向量存储
        return self.create_vector_store(chunks, store_name)
