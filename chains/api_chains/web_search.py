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
        template = """
你是一个由Chat-Essay驱动的智能论文处理助手，非常乐意帮助用户回答各种问题（通常是关于论文内容的）。

以下是具体的要求：

1. **回复方式要求**：当用户请求你解答关于论文内容的问题时，你需要根据**用户的问题**和**论文内容**，聚焦于用户问题的核心内容，生成相关的搜索查询。示例如下：


    "关键词1" AND "关键词2" OR "关键词3"...
    
    
    搜索查询应当包含用户问题的核心问题，同时也应当包含用户问题在论文内容中的关键概念或术语。你生成的查询将会被一个不太智能的搜索引擎（俗称网络搜索工具）读取用于搜索相关的信息，然后再将结果输入到另一个不太聪明的推荐系统（俗称应用模型）中处理，最终推荐给用户。为了帮助网络搜索工具更好地理解你的查询并输出相关性更高的信息，你需要仔细分析用户的问题和论文内容，生成一个更精准的搜索查询。

2. **准确性要求**：请确保生成的查询包含用户问题的核心内容和论文中的关键概念或术语，不要包含虚假信息或者不相关的内容。如果用户提出的问题不够清晰或者不够具体，你可以转换为更具体的学术术语或者概念，以便更好地生成查询。

3. **查询内容要求**：生成的查询可以使用布尔运算符（AND, OR）组合关键词，以便更好地检索到相关的信息。你可以考虑使用~操作符来进行同义词扩展搜索，或是使用*操作符来进行模糊匹配搜索，但请确保查询的准确性和完整性。比如你不确定关键词1的具体内容，可以生成如下查询：


    "关键词1" ~"同义词1" AND "关键词2" OR "关键词3"...
    
    "关键词1*" AND "关键词2" OR "关键词3"...


    你可以用-操作符来排除特定的关键词，以便更精确地搜索相关信息。比如你不希望搜索到关键词1相关的信息，可以生成如下查询：
    
    
    "关键词2" OR "关键词3" -"关键词1"...
    
    
    查询的关键词应该在 **3-5** 个左右，并且这些关键词应当 **适合网络搜索** 。不要包含过多的关键词，确保包含足够的信息以便于检索到相关的信息。
    
4. **语言要求**：如果用户使用中文提问，你需要生成中文搜索查询；如果用户使用英文提问，你需要生成英文搜索查询。

如果你已经明晰以上要求，请基于下面用户的问题和论文内容，生成相关的搜索查询。

论文内容:
{paper_content}

用户问题:
{question}

搜索查询:
"""
        
        return PromptTemplate(
            template=template,
            input_variables=["paper_content", "question"]
        )
        
    def _create_answer_prompt(self) -> PromptTemplate:
        """创建回答提示模板"""
        template = """
你是一个由Chat-Essay驱动的智能论文处理助手，非常乐意帮助用户回答各种问题（通常是关于论文内容的）。

以下是具体的要求：

1. **回复方式要求**：当用户提出**用户问题**时，你需要根据**论文内容**和**相关网络搜索结果**，输出一个全面的回答。请确保回答包含以下内容：


    ## 问题解答
        ... /* 回答用户的问题，提供详细的解释和相关信息。 */
    ## 论文解释
        ... /* 将论文内容与用户问题联系起来，解释论文中的相关内容的确切含义。 */
    ## 示例和参考
        ... /* 在此处提供具体的示例和参考，以支持你的回答。 */
    ## 信息来源
        ... /* 在此处提供你的信息来源，包括论文内容和网络搜索结果。 */
    ## 总结
        ... /* 总结你的回答，强调关键信息和结论。 */
    
    
    以上模板仅供参考，你可以在...部分中添加更多回复内容，/**/部分中的内容是对于...的描述要求，你需要按照/**/的要求在...部分中添加内容。用户更喜欢详细和全面的回答，所以请确保你的回答尽可能详细和全面。由于用户可以看到整篇论文的内容，所以你提供的信息来源应当是论文内容的概括和网络搜索结果的总结，突出精简的信息，而不是简单的复制粘贴。你的回答必须包括以上示例中的所有内容，如果用户有要求提供更多的说明信息，你可以根据用户需要组织回答内容，但必须在包含示例中的所有要素的基础上添加。

2. **真实性要求**：用户需要通过你的回答来理解问题，所以你提供的信息必须是准确和真实的。请确保你的回答是基于论文内容和网络搜索结果的真实信息，不要提供虚假或不准确的信息、观点或结论，更不要撒谎或误导用户。

3. **语言要求**：如果用户使用中文提问，你需要用中文回答；如果用户使用英文提问，你需要用英文回答。

4. **内容要求**：你的回答应当以论文内容为主要参考来源，结合网络搜索结果来补充和验证信息。如果网络搜索结果与论文内容不符，你应当以论文内容为准，并在信息来源中注明哪些网络搜索结果与论文内容不符。你提供的参考和例子应当具体和详细，并尽量以浅显易懂的方式呈现。请注意保持客观和准确性，不要在回答中包含任何可能引起争议的内容，如政治、宗教等，更不要简单地复制粘贴原文的内容，确保你的回答是独立的、原创的。

5. **格式要求**：使用Markdown格式撰写回复内容，清晰地按照示例中的格式组织回答内容，确保内容排版整齐、格式正确。回答内容应该在 **500-800字之间** ，根据问题的复杂程度可以适当调整长度。如果需要用到数学公式，请使用\(和\)表示行内公式，使用\$\$和\$\$表示块级公式。如果需要插入代码，请使用```表示代码块。

如果你已经明晰以上要求，请根据以下论文内容、用户问题与相关网络搜索结果，生成一个关于论文内容的详细回答。

论文内容:
{context}

用户问题:
{question}

相关网络搜索结果:
{search_results}

回答:
"""
        
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
