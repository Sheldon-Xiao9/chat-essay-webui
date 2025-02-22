from typing import List, Dict, Any, Optional
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from utils.model_loader import ModelLoader
from utils.vectorizer import Vectorizer

class SummaryChain:
    """摘要写作的RAG链"""
    
    def __init__(self):
        self._model_loader = None
        self._vectorizer = None
        self._chat_model = None
        self._vector_store_cache = {}  # 缓存vector store

    def clear_cache(self, file_path: Optional[str] = None):
        """清理缓存
        如果指定file_path，只清理该文件的缓存
        否则清理所有缓存
        """
        if file_path is None:
            print("[SummaryChain] Clearing all caches")
            self._vector_store_cache.clear()
        elif file_path in self._vector_store_cache:
            print(f"[SummaryChain] Clearing cache for {file_path}")
            del self._vector_store_cache[file_path]
        
    @property
    def model_loader(self):
        if self._model_loader is None:
            self._model_loader = ModelLoader()
        return self._model_loader

    @property
    def vectorizer(self):
        if self._vectorizer is None:
            self._vectorizer = Vectorizer()
        return self._vectorizer

    @property
    def llm(self):
        """获取聊天模型"""
        if self._chat_model is None:
            self._chat_model = self.model_loader.load_chat_model()
        return self._chat_model
        
    def _create_prompt_template(self) -> PromptTemplate:
        """创建提示模板"""
        template = """根据以下文档内容和用户请求，生成一个准确、连贯的摘要。

文档内容:
{context}

用户请求:
{query}

请根据文档内容和用户的具体要求，生成一个恰当的摘要。摘要应该：
1. 符合用户的具体要求
2. 准确反映原文的主要内容
3. 结构清晰、表述准确
4. 保持适当的长度

摘要:
"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "query"]
        )

    def get_or_create_vector_store(self, file_path: str) -> Any:
        """获取或创建向量存储"""
        store_name = f"summary_{hash(file_path)}"
        
        # 先检查内存缓存
        if file_path in self._vector_store_cache:
            print("[SummaryChain] Using cached vector store")
            return self._vector_store_cache[file_path]
            
        # 再检查磁盘缓存
        vector_store = self.vectorizer.load_vector_store(store_name)
        if vector_store is not None:
            print("[SummaryChain] Loaded vector store from disk")
            self._vector_store_cache[file_path] = vector_store
            return vector_store
            
        # 都没有则创建新的
        print("[SummaryChain] Creating new vector store")
        # 清理旧的缓存和文件
        self.clear_cache(file_path)
        vector_store = self.vectorizer.process_file(file_path, store_name)
        self._vector_store_cache[file_path] = vector_store
        return vector_store
        
    def create_chain(self, vector_store):
        """创建生成摘要的LLM链"""
        print("[SummaryChain] Creating chain...")
        prompt = self._create_prompt_template()
        chain = LLMChain(llm=self.llm, prompt=prompt)
        print("[SummaryChain] Chain created")
        return chain, vector_store
    
    def process_file(self, file_path: str, query: str) -> Dict[str, Any]:
        """处理文件并生成摘要"""
        try:
            print("\n[SummaryChain] Processing file:", file_path)
            print("[SummaryChain] Query:", query)
            
            # 获取或创建向量存储
            vector_store = self.get_or_create_vector_store(file_path)
            
            # 创建链
            print("[SummaryChain] Setting up chain...")
            chain, vector_store = self.create_chain(vector_store)
            
            # 检索相关内容
            print("[SummaryChain] Retrieving relevant documents...")
            docs = vector_store.similarity_search(query, k=3)
            context = "\n\n".join([doc.page_content for doc in docs])
            print("[SummaryChain] Retrieved context length:", len(context))
            
            # 执行生成
            print("[SummaryChain] Running chain...")
            print("[SummaryChain] Input parameters:")
            print(f"- context length: {len(context)}")
            print(f"- query: {query}")
            
            try:
                inputs = {
                    "context": context,
                    "query": query
                }
                print("[SummaryChain] Calling chain.predict with:", inputs)
                
                result = chain.predict(**inputs)
                print("[SummaryChain] Chain completed successfully")
                print("[SummaryChain] Result type:", type(result))
                print("[SummaryChain] Result length:", len(str(result)))
                
                return {
                    "success": True,
                    "summary": result
                }
            except Exception as e:
                print("[SummaryChain] Error during prediction:", str(e))
                raise
            
        except Exception as e:
            print("[SummaryChain] Error:", str(e))
            return {
                "success": False,
                "error": str(e)
            }
