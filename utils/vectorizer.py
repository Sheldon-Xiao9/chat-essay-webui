import os
import time
import shutil
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from langchain_community.vectorstores import FAISS
from utils.model_loader import ModelLoader
from utils.file_processor import FileProcessor

class Vectorizer:
    """向量化处理工具类"""
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.file_processor = FileProcessor()
        self.embedding_model = self.model_loader.load_embedding_model()
        self._vector_stores: Dict[str, FAISS] = {}  # 内存缓存，添加类型注解
        
    def cleanup_expired_stores(self):
        """清理过期的向量存储"""
        vector_store_dir = "database/vector_store"
        if not os.path.exists(vector_store_dir):
            os.makedirs(vector_store_dir, exist_ok=True)
            return

        # 检查并清理过期文件
        current_time = time.time()
        for store_name in os.listdir(vector_store_dir):
            store_path = os.path.join(vector_store_dir, store_name)
            if not os.path.isdir(store_path):
                continue
                
            # 如果超过24小时就清理
            last_modified = os.path.getmtime(store_path)
            if current_time - last_modified > 24 * 3600:
                try:
                    shutil.rmtree(store_path)
                    print(f"[Vectorizer] Cleaned up expired store: {store_name}")
                except Exception as e:
                    print(f"[Vectorizer] Error cleaning up store {store_name}: {e}")
                    
        # 清理内存缓存中的过期项
        expired_keys = []
        for file_path in self._vector_stores:
            store_name = f"summary_{hash(file_path)}"
            store_path = os.path.join(vector_store_dir, store_name)
            if not os.path.exists(store_path):
                expired_keys.append(file_path)
                
        for key in expired_keys:
            del self._vector_stores[key]
            print(f"[Vectorizer] Removed expired store from memory: {key}")

    def clear_file_cache(self, file_path: str) -> None:
        """清理指定文件的缓存"""
        print(f"[Vectorizer] Clearing cache for: {file_path}")
        
        # 清理内存缓存
        if file_path in self._vector_stores:
            del self._vector_stores[file_path]
            print("[Vectorizer] Cleared memory cache")
            
        # 清理磁盘缓存
        store_name = f"summary_{hash(file_path)}"
        store_path = os.path.join("database/vector_store", store_name)
        if os.path.exists(store_path):
            try:
                shutil.rmtree(store_path)
                print("[Vectorizer] Cleared disk cache")
            except Exception as e:
                print(f"[Vectorizer] Error clearing disk cache: {e}")
    
    def get_store_path(self, file_path: str) -> str:
        """获取向量存储路径"""
        store_name = f"summary_{hash(file_path)}"
        return os.path.join("database/vector_store", store_name)
        
    def create_vector_store(self, texts: List[str], store_name: str) -> FAISS:
        """创建向量存储"""
        print(f"\n[Vectorizer] Creating vector store: {store_name}")
        
        if not texts:
            raise ValueError("[Vectorizer] No texts provided for vectorization")
            
        try:
            # 创建向量存储
            print("[Vectorizer] Converting texts to vectors...")
            start_time = time.time()
            vector_store = FAISS.from_texts(texts, self.embedding_model)
            print(f"[Vectorizer] Conversion completed in {time.time() - start_time:.2f}s")
            
            # 保存到磁盘
            store_path = os.path.join("database/vector_store", store_name)
            print(f"[Vectorizer] Saving to: {store_path}")
            os.makedirs("database/vector_store", exist_ok=True)
            vector_store.save_local(store_path)
            
            return vector_store
            
        except Exception as e:
            print(f"[Vectorizer] Error creating vector store: {str(e)}")
            raise Exception(f"Error creating vector store: {str(e)}")
    
    def load_vector_store(self, store_name: str) -> Optional[FAISS]:
        """加载向量存储"""
        store_path = os.path.join("database/vector_store", store_name)
        
        if not os.path.exists(store_path):
            return None
            
        try:
            print(f"[Vectorizer] Loading from: {store_path}")
            vector_store = FAISS.load_local(store_path, self.embedding_model)
            return vector_store
            
        except Exception as e:
            print(f"[Vectorizer] Error loading vector store: {str(e)}")
            return None
    
    def process_file(self, file_path: str, store_name: str) -> FAISS:
        """处理文件并创建向量存储"""
        try:
            print(f"\n[Vectorizer] Processing file: {file_path}")
            
            # 检查内存缓存
            if file_path in self._vector_stores:
                print("[Vectorizer] Using memory cached store")
                return self._vector_stores[file_path]
                
            # 检查磁盘缓存
            store_path = os.path.join("database/vector_store", store_name)
            if os.path.exists(store_path):
                print("[Vectorizer] Loading from disk cache")
                vector_store = self.load_vector_store(store_name)
                if vector_store:
                    self._vector_stores[file_path] = vector_store
                    return vector_store
            
            # 加载文档并处理
            print("[Vectorizer] Loading document...")
            texts = self.file_processor.load_document(file_path)
            
            # 分块
            print("[Vectorizer] Splitting text...")
            chunks = []
            for text in texts:
                chunks.extend(self.file_processor.split_text(text))
            print(f"[Vectorizer] Created {len(chunks)} chunks")
            
            # 创建向量存储
            vector_store = self.create_vector_store(chunks, store_name)
            
            # 缓存到内存
            self._vector_stores[file_path] = vector_store
            
            return vector_store
            
        except Exception as e:
            print(f"[Vectorizer] Error processing file: {str(e)}")
            raise Exception(f"Error processing file: {str(e)}")
