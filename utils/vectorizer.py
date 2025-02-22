import os
import time
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from utils.model_loader import ModelLoader
from utils.file_processor import FileProcessor

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
        print(f"\n[Vectorizer] Creating vector store: {store_name}")
        print(f"[Vectorizer] Input texts count: {len(texts)}")
        
        if not texts:
            raise ValueError("No texts provided for vectorization")
            
        try:
            start_time = time.time()
            # 创建向量存储
            print("[Vectorizer] Converting texts to vectors...")
            vector_store = FAISS.from_texts(
                texts,
                self.embedding_model
            )
            conversion_time = time.time() - start_time
            print(f"[Vectorizer] Vector conversion completed in {conversion_time:.2f} seconds")
            
            # 确保vector_store目录存在
            print("[Vectorizer] Ensuring storage directory exists...")
            os.makedirs("database/vector_store", exist_ok=True)
            
            # 保存向量存储
            store_path = f"database/vector_store/{store_name}"
            print(f"[Vectorizer] Saving vectors to: {store_path}")
            vector_store.save_local(store_path)
            print("[Vectorizer] Vector store saved successfully")
            
            return vector_store
            
        except Exception as e:
            print(f"[Vectorizer] Error creating vector store: {str(e)}")
            raise Exception(f"Error creating vector store: {str(e)}")
    
    def load_vector_store(self, store_name: str) -> Optional[FAISS]:
        """
        加载向量存储
        """
        print(f"\n[Vectorizer] Attempting to load vector store: {store_name}")
        store_path = f"database/vector_store/{store_name}"
        
        if not os.path.exists(store_path):
            print(f"[Vectorizer] Store not found: {store_path}")
            return None
            
        try:
            print("[Vectorizer] Loading vector store from disk...")
            start_time = time.time()
            vector_store = FAISS.load_local(
                store_path,
                self.embedding_model
            )
            load_time = time.time() - start_time
            print(f"[Vectorizer] Vector store loaded in {load_time:.2f} seconds")
            return vector_store
            
        except Exception as e:
            print(f"[Vectorizer] Error loading vector store: {str(e)}")
            raise Exception(f"Error loading vector store: {str(e)}")
    
    def process_file(self, file_path: str, store_name: str) -> FAISS:
        """
        处理文件并创建向量存储
        """
        print(f"\n[Vectorizer] Processing file: {file_path}")
        print(f"[Vectorizer] Using store name: {store_name}")
        
        # 加载文档
        print("[Vectorizer] Loading document...")
        start_time = time.time()
        texts = self.file_processor.load_document(file_path)
        load_time = time.time() - start_time
        print(f"[Vectorizer] Document loaded in {load_time:.2f} seconds")
        print(f"[Vectorizer] Document pages: {len(texts)}")
        
        # 文本分块
        print("[Vectorizer] Splitting text into chunks...")
        chunks = []
        for i, text in enumerate(texts):
            new_chunks = self.file_processor.split_text(text)
            chunks.extend(new_chunks)
            print(f"[Vectorizer] Page {i+1}: split into {len(new_chunks)} chunks")
        print(f"[Vectorizer] Total chunks created: {len(chunks)}")
        
        # 创建向量存储
        print("[Vectorizer] Starting vector store creation...")
        store = self.create_vector_store(chunks, store_name)
        print("[Vectorizer] File processing completed")
        return store
