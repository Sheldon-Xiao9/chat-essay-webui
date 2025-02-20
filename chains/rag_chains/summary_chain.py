from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from utils.model_loader import ModelLoader
from utils.vectorizer import Vectorizer

class SummaryChain:
    """摘要写作的RAG链"""
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.vectorizer = Vectorizer()
        self.llm = self.model_loader.load_chat_model()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
    def _create_prompt_template(self) -> PromptTemplate:
        """创建提示模板"""
        template = """根据以下文档内容和用户请求，生成一个准确、连贯的摘要。

文档内容:
{context}

用户请求:
{question}

请根据文档内容和用户的具体要求，生成一个恰当的摘要。摘要应该：
1. 符合用户的具体要求
2. 准确反映原文的主要内容
3. 结构清晰、表述准确
4. 保持适当的长度

摘要:
"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
    def create_retrieval_chain(self, vector_store):
        """创建检索链"""
        prompt = self._create_prompt_template()
        
        chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(
                search_kwargs={"k": 3}
            ),
            chain_type_kwargs={
                "prompt": prompt,
                "memory": self.memory,
            },
            return_source_documents=True,
        )
        
        return chain
    
    def process_file(self, file_path: str, query: str) -> Dict[str, Any]:
        """处理文件并生成摘要"""
        try:
            # 向量化处理文件
            store_name = f"summary_{hash(file_path)}"
            vector_store = self.vectorizer.process_file(file_path, store_name)
            
            # 创建检索链
            chain = self.create_retrieval_chain(vector_store)
            
            # 执行检索和生成
            result = chain({"query": query})
            
            return {
                "success": True,
                "summary": result["result"],
                "sources": [doc.page_content for doc in result["source_documents"]]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
