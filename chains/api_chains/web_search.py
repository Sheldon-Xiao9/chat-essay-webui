from typing import List, Dict, Any
import json
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.tools import DuckDuckGoSearchRun
from utils.model_loader import ModelLoader
from utils.vectorizer import Vectorizer

class WebSearchChain:
    """论文阅读的网页搜索链"""
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.vectorizer = Vectorizer()
        self.llm = self.model_loader.load_chat_model()
        self.search_tool = DuckDuckGoSearchRun()  # 使用DuckDuckGo搜索
        self._vector_stores = {}  # 缓存向量存储
        
    def _create_search_prompt(self) -> PromptTemplate:
        """创建搜索提示模板"""
        template = """基于用户的问题和论文内容，生成相关的搜索查询。

论文内容:
{paper_content}

用户问题:
{question}

请生成2-3个相关的搜索查询，每个查询应该：
1. 聚焦于用户问题的核心内容
2. 包含论文中的关键概念或术语
3. 使用精确的学术术语
4. 适合网络搜索

搜索查询:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["paper_content", "question"]
        )
        
    def _create_answer_prompt(self) -> PromptTemplate:
        """创建回答提示模板"""
        template = """基于以下信息回答用户的问题。

论文内容:
{context}

用户问题:
{question}

相关网络搜索结果:
{search_results}

请提供一个全面的回答：
1. 主要基于论文中的相关内容回答
2. 用网络搜索结果补充和验证信息
3. 提供具体的参考和例子
4. 保持客观和准确性
5. 清晰地组织信息

回答:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question", "search_results"]
        )
    
    def _get_or_create_vector_store(self, file_path: str, paper_content: str):
        """获取或创建向量存储"""
        store_name = f"paper_{hash(file_path)}"
        
        # 检查缓存
        if file_path in self._vector_stores:
            print("[WebSearchChain] Using cached vector store")
            return self._vector_stores[file_path]
            
        print("[WebSearchChain] Creating new vector store...")
        vector_store = self.vectorizer.process_file(file_path, store_name)
        self._vector_stores[file_path] = vector_store
        return vector_store
    
    def _generate_search_queries(self, paper_content: str, question: str) -> List[str]:
        """生成搜索查询"""
        search_prompt = self._create_search_prompt()
        search_chain = LLMChain(llm=self.llm, prompt=search_prompt)
        
        # 生成搜索查询
        result = search_chain.run({
            "paper_content": paper_content,
            "question": question
        })
        
        # 将结果分割成多个查询
        queries = [q.strip() for q in result.split('\n') if q.strip()]
        return queries[:3]  # 最多返回3个查询
        
    def _perform_searches(self, queries: List[str]) -> str:
        """执行搜索查询"""
        all_results = []
        
        for query in queries:
            try:
                results = self.search_tool.run(query)
                all_results.append(results)
            except Exception as e:
                print(f"[WebSearchChain] Search error for query '{query}': {str(e)}")
                
        return "\n\n".join(all_results)
        
    def process_paper(self, file_path: str, paper_content: str, question: str) -> Dict[str, Any]:
        """处理论文并回答问题"""
        try:
            print(f"\n[WebSearchChain] Processing question about: {file_path}")
            print(f"[WebSearchChain] Question: {question}")
            
            # 获取或创建向量存储
            vector_store = self._get_or_create_vector_store(file_path, paper_content)
            
            # 从论文中检索相关内容
            print("[WebSearchChain] Retrieving relevant content from paper...")
            docs = vector_store.similarity_search(question, k=3)
            context = "\n\n".join([doc.page_content for doc in docs])
            print(f"[WebSearchChain] Retrieved {len(docs)} relevant sections")
            
            # 生成并执行搜索
            print("[WebSearchChain] Generating search queries...")
            queries = self._generate_search_queries(context, question)
            print("[WebSearchChain] Performing web searches...")
            search_results = self._perform_searches(queries)
            
            # 创建回答链
            print("[WebSearchChain] Generating answer...")
            answer_prompt = self._create_answer_prompt()
            answer_chain = LLMChain(llm=self.llm, prompt=answer_prompt)
            
            # 生成回答
            answer = answer_chain.run({
                "context": context,
                "question": question,
                "search_results": search_results
            })
            
            return {
                "success": True,
                "answer": answer,
                "context": context,
                "search_results": search_results
            }
            
        except Exception as e:
            print(f"[WebSearchChain] Error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
