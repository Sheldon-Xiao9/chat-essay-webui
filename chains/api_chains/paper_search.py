from typing import List, Dict, Any
import requests
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from utils.model_loader import ModelLoader

class PaperSearchChain:
    """文献推荐的搜索链"""
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.llm = self.model_loader.load_chat_model()
        self.crossref_api = "https://api.crossref.org/works"
        self.headers = {
            "User-Agent": "ChatEssayWebUI/1.0 (mailto:your-email@domain.com)"
        }
        
    def _create_search_prompt(self) -> PromptTemplate:
        """创建搜索提示模板"""
        template = """基于用户的研究问题，生成精确的学术搜索查询。

研究问题:
{question}

请生成一个学术搜索查询，该查询应该：
1. 包含关键的学术术语和概念
2. 使用布尔运算符（AND, OR）组合关键词
3. 考虑同义词或相关概念
4. 适合学术文献检索

搜索查询:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["question"]
        )
        
    def _create_filter_prompt(self) -> PromptTemplate:
        """创建过滤提示模板"""
        template = """基于用户的研究问题和检索到的论文列表，筛选最相关的论文。

研究问题:
{question}

论文列表:
{papers}

请选择3-5篇最相关的论文，并说明选择理由。考虑以下因素：
1. 与研究问题的相关性
2. 论文的影响力和引用次数
3. 发表时间的新近性
4. 研究方法的可靠性

推荐论文:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["question", "papers"]
        )
    
    def _search_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """搜索论文"""
        try:
            params = {
                "query": query,
                "rows": max_results,
                "sort": "relevance",
                "select": "DOI,title,author,published-print,abstract",
            }
            
            response = requests.get(
                self.crossref_api,
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            
            results = []
            for item in response.json()["message"]["items"]:
                # 提取所需信息
                paper = {
                    "title": item.get("title", [""])[0],
                    "authors": [
                        author.get("given", "") + " " + author.get("family", "")
                        for author in item.get("author", [])
                    ],
                    "year": item.get("published-print", {}).get("date-parts", [[0]])[0][0],
                    "doi": item.get("DOI", ""),
                    "abstract": item.get("abstract", "No abstract available")
                }
                results.append(paper)
                
            return results
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    def _format_papers(self, papers: List[Dict]) -> str:
        """格式化论文信息"""
        formatted = []
        for i, paper in enumerate(papers, 1):
            paper_info = (
                f"{i}. 标题: {paper['title']}\n"
                f"   作者: {', '.join(paper['authors'])}\n"
                f"   年份: {paper['year']}\n"
                f"   DOI: {paper['doi']}\n"
                f"   摘要: {paper['abstract'][:300]}...\n"
            )
            formatted.append(paper_info)
        return "\n\n".join(formatted)
    
    def search(self, question: str) -> Dict[str, Any]:
        """搜索和推荐论文"""
        try:
            # 生成搜索查询
            search_prompt = self._create_search_prompt()
            search_chain = LLMChain(llm=self.llm, prompt=search_prompt)
            query = search_chain.run({"question": question})
            
            # 搜索论文
            papers = self._search_papers(query)
            if not papers:
                return {
                    "success": False,
                    "error": "No papers found"
                }
            
            # 格式化论文信息
            formatted_papers = self._format_papers(papers)
            
            # 筛选论文
            filter_prompt = self._create_filter_prompt()
            filter_chain = LLMChain(llm=self.llm, prompt=filter_prompt)
            recommendations = filter_chain.run({
                "question": question,
                "papers": formatted_papers
            })
            
            return {
                "success": True,
                "recommendations": recommendations,
                "all_papers": papers
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
