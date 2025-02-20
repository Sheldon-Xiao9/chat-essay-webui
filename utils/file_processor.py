import os
from typing import List, Optional
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)

class FileProcessor:
    """文件处理工具类"""
    
    @staticmethod
    def load_document(file_path: str) -> List[str]:
        """
        根据文件类型加载文档
        支持: .txt, .pdf, .docx
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                return [doc.page_content for doc in documents]
                
            elif file_extension == '.txt':
                loader = TextLoader(file_path, encoding='utf-8')
                documents = loader.load()
                return [doc.page_content for doc in documents]
                
            elif file_extension == '.docx':
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
                return [doc.page_content for doc in documents]
                
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Error loading document: {str(e)}")
    
    @staticmethod
    def split_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        将文本分割成更小的块
        """
        if not text:
            return []
            
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
        return chunks
