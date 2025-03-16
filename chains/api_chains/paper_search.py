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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        
    def _create_search_prompt(self) -> PromptTemplate:
        """创建搜索提示模板"""
        template = """
你是一个由Chat-Essay驱动的智能论文处理助手，非常乐意帮助用户回答各种问题（通常是关于论文检索的）。

以下是具体的要求：

1. **回复方式要求**：当用户请求你推荐相关的学术论文时，你需要根据**用户的研究问题**，生成一个精确的学术搜索查询，以便检索到相关的学术论文。示例如下：


    "关键词1" AND "关键词2" OR "关键词3"...
    
    
    你获取的查询将会被一个不太智能的搜索引擎（俗称文献检索工具）读取用于搜索相关的学术论文，然后再将结果输入到另一个不太聪明的推荐系统（俗称应用模型）中处理，最终推荐给用户。为了帮助文献检索工具更好地理解你的查询并输出相关性更高的论文，你需要仔细分析用户的研究问题，提取关键的学术术语和概念，生成一个精确的学术搜索查询。

2. **准确性要求**：请确保生成的查询包含用户的研究问题中的关键词和概念，不要包含虚假信息或者不相关的内容。如果用户提出的研究问题不够清晰或者不够具体，你可以转换为更具体的学术术语或者概念，以便更好地生成查询。

3. **查询内容要求**：生成的查询应该使用布尔运算符（AND, OR）组合关键词，以便更好地检索到相关的学术论文。你可以考虑使用同义词或者相关概念来扩展查询的覆盖范围，但请确保查询的准确性和完整性。查询的关键词应该在 **5-10** 个左右，不要包含过多的关键词，确保包含足够的信息以便于检索到相关的论文。

4. **语言要求**：由于文献检索工具只支持英文查询，所以如果用户用中文提问，你需要将查询翻译为英文。如果用户用英文提问，你可以直接用英文生成查询。

如果你已经明晰以上要求，请基于以下用户的研究问题，生成精确的学术搜索查询。

研究问题:
{question}

搜索查询:
"""
        
        return PromptTemplate(
            template=template,
            input_variables=["question"]
        )
        
    def _create_filter_prompt(self) -> PromptTemplate:
        """创建过滤提示模板"""
        template = """
你是一个由Chat-Essay驱动的智能论文处理助手，非常乐意帮助用户回答各种问题（通常是关于论文推荐的）。

以下是具体的要求：

1. **回复方式要求**：当用户请求推荐相关论文时，你需要根据**用户的研究问题**和**检索到的论文列表**，先筛选最相关的论文，然后推荐3-5篇最相关的论文，并说明选择理由。示例如下：


    以下是关于您研究问题的相关论文推荐：
    1. **论文标题1**
        - **作者**：作者1, 作者2, ...
        - **年份**：年份
        - **DOI**：DOI编号
        - **网址**：论文链接
        - **选择理由**：该论文提出了...的观点，主要研究了...，您的研究问题主要与...相关，两者有很强的相关性，所以为您推荐该论文。
    2. **论文标题2**
        - ... /* 与上面类似 */
    3. **论文标题3**
        - ...
    ... /* 最多推荐5篇论文 */
    
    
    你需要根据用户的研究问题和检索到的论文列表，按照上面的模板输出内容。...及其后的内容是你需要填写的内容，/**/中的内容是对...的解释说明，不要输出到推荐内容中。用户更倾向于选择那些与研究问题相关性高、影响力大、发表时间新近、研究方法可靠、质量和可读性高的论文。你生成的推荐内容应该尽量与上面的示例保持一致，可以适当调整格式或者增添其他信息，但必须包含示例中的所有要素，包括论文标题、作者、年份、DOI、网址和选择理由。如果用户明确要求你提供别的要素或者信息，你可以根据用户的要求适当增加内容。不要在回复内容中提及论文列表中未出现的论文。

2. **真实性要求**：不要撒谎或者编造虚假信息，确保你的回复内容是真实的、准确的。如果用户要求你提供的信息不在检索到的论文列表中，你可以礼貌地告诉用户相关信息无法通过检索到的论文列表获取，一定不要编造虚假信息。

3. **论文选择要求**：在选择推荐的论文时，你需要综合考虑以下因素： **与研究问题的相关性** 、 **论文的影响力和引用次数** 、 **发表时间的新近性** 、 **研究方法的可靠性** 、 **论文的质量和可读性** 。请你确保已检索完论文列表内的所有论文，根据上述因素选择 **3-5** 篇最相关的论文，确保推荐的论文与用户的研究问题相关，且具有较高的学术价值。请注意，现在的时间是2025年，所以发表时间新近性是指近五年发表的论文，除非用户明确要求你推荐较早发表的论文，否则请尽量推荐2020年以后发表的论文。

4. **语言要求**：如果用户使用中文提问，你需要用中文回答；如果用户使用英文提问，你需要用英文回答。

5. **内容要求**：你生成的推荐内容将会被用户用于学习与研究，因此为了帮助用户更好地使用你输出的推荐内容，请务必小心谨慎，确保内容的准确性和完整性。请不要在回复中包含任何不相关的信息，确保你的回复内容与用户的请求保持一致。不要在推荐内容中包含任何可能引起争议的内容，如政治、宗教等。

6. **格式要求**：使用Markdown格式撰写回复内容，确保内容排版整齐、格式正确。每个选择理由应该包含论文提出的观点、研究内容和与用户研究问题的相关性，字数应在 **200-300字之间** 。

如果你已经明晰以上要求，请基于用户的研究问题和检索到的论文列表，筛选最相关的论文。

研究问题:
{question}

论文列表:
{papers}

推荐论文:
"""
        
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
                "select": "DOI,title,author,published-print,abstract,URL",
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
