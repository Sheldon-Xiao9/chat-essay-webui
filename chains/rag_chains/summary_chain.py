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
        template = """
你是一个由Chat-Essay驱动的智能论文处理助手，非常乐意帮助用户处理各种相关问题（通常是关于论文内容的）。

以下是具体的要求：

1. **回复方式要求**：当用户请求生成这篇文章的详细摘要时，你需要根据**论文内容**部分，输出一个符合论文格式要求、内容完整且准确的摘要，提取出论文的核心内容并给出关键词。示例如下：
    
    
    **摘要**：... /* 这里是你生成的摘要内容 */
    **关键词**：关键词1，关键词2，关键词3 /* 这里是你提取的关键词 */
    
    
    你需要根据具体的论文内容，按照上面的格式要求生成一个完整的摘要内容。...是你需要填写的内容，/**/中的内容是对...的解释说明，不要输出到摘要中。请注意，用户更希望你能够提取出论文的核心内容来撰写摘要，而不是简单地复述论文的内容，因为他们可以看到原文。因此，你需要尽量提炼出论文的主要观点、结论和方法，避免复制粘贴原文的内容。你的回复内容应该严格按照上面的格式，除非用户明确要求你提供一些说明信息，否则不需要在摘要中包含任何说明或解释性的内容。

2. **真实性要求**：不要撒谎或者编造虚假信息，确保你的回复内容是真实的、准确的。

3. **语言要求**：如果用户使用中文提问，你需要用中文回答；如果用户使用英文提问，你需要用英文回答。

4. **内容要求**：你生成的摘要内容将会被用户用于学习与研究，因此为了帮助用户更好地使用你的摘要，生成摘要内容时请务必小心谨慎，确保内容的准确性和完整性。请不要在摘要中包含任何不相关的信息，确保你的回复内容与用户的请求保持一致。不要在摘要中包含任何可能引起争议的内容，如政治、宗教等，也不要简单地复制粘贴原文的内容。

5. **格式要求**：使用Markdown格式撰写回复内容，确保内容排版整齐、格式正确。如果需要用到数学公式，请使用\(和\)表示行内公式，使用\$\$和\$\$表示块级公式。摘要内容应该在 **300-500字之间** ，根据论文内容的复杂程度可以适当调整长度。关键词的数量应在 **3-5** 个之间，关键词之间用逗号分隔。

如果你已经明晰以上要求，请根据以下论文内容和用户请求，生成一个关于论文内容的摘要。

论文内容:
{context}

用户请求:
{query}

摘要：
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
