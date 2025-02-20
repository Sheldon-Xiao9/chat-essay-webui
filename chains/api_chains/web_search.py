from typing import List, Dict, Any
import json
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.tools import DuckDuckGoSearchRun
from utils.model_loader import ModelLoader

class WebSearchChain:
    """论文阅读的网页搜索链"""
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.llm = self.model_loader.load_chat_model()
        self.search_tool = DuckDuckGoSearchRun()
        
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
{paper_content}

用户问题:
{question}

相关搜索结果:
{search_results}

请提供一个全面的回答：
1. 结合论文内容和搜索结果
2. 重点关注用户问题的核心内容
3. 提供具体的参考和例子
4. 保持客观和准确性
5. 清晰地组织信息

回答:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["paper_content", "question", "search_results"]
        )
    
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
                print(f"Search error for query '{query}': {str(e)}")
                
        return "\n\n".join(all_results)
        
    def process_paper(self, paper_content: str, question: str) -> Dict[str, Any]:
        """处理论文并回答问题"""
        try:
            # 生成搜索查询
            queries = self._generate_search_queries(paper_content, question)
            
            # 执行搜索
            search_results = self._perform_searches(queries)
            
            # 创建回答链
            answer_prompt = self._create_answer_prompt()
            answer_chain = LLMChain(llm=self.llm, prompt=answer_prompt)
            
            # 生成回答
            answer = answer_chain.run({
                "paper_content": paper_content,
                "question": question,
                "search_results": search_results
            })
            
            return {
                "success": True,
                "answer": answer,
                "search_results": search_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
