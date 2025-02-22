from fastapi import APIRouter, HTTPException, File, UploadFile, Request
from fastapi.responses import JSONResponse
import os
import uuid
from typing import Dict, Any, Optional
from chains.rag_chains.summary_chain import SummaryChain
from chains.api_chains.web_search import WebSearchChain
from chains.api_chains.paper_search import PaperSearchChain
from utils.file_processor import FileProcessor
from utils.model_loader import ModelLoader

router = APIRouter()

# 全局实例管理器
class ProcessorManager:
    _instance = None
    _file_processor = None
    _model_loader = None
    _summary_chain = None
    _web_search_chain = None
    _paper_search_chain = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ProcessorManager()
        return cls._instance

    @property
    def file_processor(self):
        if self._file_processor is None:
            self._file_processor = FileProcessor()
        return self._file_processor

    @property
    def model_loader(self):
        if self._model_loader is None:
            self._model_loader = ModelLoader()
        return self._model_loader

    @property
    def summary_chain(self):
        if self._summary_chain is None:
            self._summary_chain = SummaryChain()
        return self._summary_chain

    @property
    def web_search_chain(self):
        if self._web_search_chain is None:
            self._web_search_chain = WebSearchChain()
        return self._web_search_chain

    @property
    def paper_search_chain(self):
        if self._paper_search_chain is None:
            self._paper_search_chain = PaperSearchChain()
        return self._paper_search_chain

    def cleanup(self):
        """清理所有资源"""
        if self._model_loader:
            try:
                self._model_loader.cleanup()
                print("模型资源已清理")
            except Exception as e:
                print(f"清理模型资源时出错: {str(e)}")
        self._file_processor = None
        self._model_loader = None
        self._summary_chain = None
        self._web_search_chain = None
        self._paper_search_chain = None

processor_manager = ProcessorManager.get_instance()

def get_model_loader() -> Optional[ModelLoader]:
    """获取ModelLoader实例，用于清理资源"""
    return processor_manager.model_loader

def get_summary_chain() -> Optional[SummaryChain]:
    """获取SummaryChain实例"""
    return processor_manager.summary_chain

# 确保database目录存在
DATABASE_DIR = "database"
os.makedirs(DATABASE_DIR, exist_ok=True)

@router.post("/summary")
async def generate_summary(request: Request):
    """生成文档摘要"""
    try:
        data = await request.json()
        file_path = data.get("file_path", "")
        query = data.get("content", "")
        
        if file_path and file_path.startswith("/database/"):
            # 如果提供了文件路径，处理文件摘要
            real_path = os.path.join(os.getcwd(), file_path.lstrip("/"))
            
            # 获取或创建chain实例
            chain = processor_manager.summary_chain
            
            # 处理文件
            if data.get("isNewUpload"):
                print("[API] New file uploaded, clearing cache...")
                chain.clear_cache(real_path)
                
            # 生成摘要    
            result = chain.process_file(real_path, query)
        else:
            # 如果没有文件路径，直接处理文本查询
            response = processor_manager.summary_chain.llm(query)
            result = {
                "success": True,
                "summary": response
            }
            
        return JSONResponse(result)
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

@router.post("/read-paper")
async def read_paper(request: Request):
    """阅读论文并回答问题"""
    try:
        data = await request.json()
        file_path = data.get("file_path", "")
        question = data.get("content", "")
        
        if file_path and file_path.startswith("/database/"):
            # 如果提供了文件路径，结合文件内容回答问题
            real_path = os.path.join(os.getcwd(), file_path.lstrip("/"))
            print(f"[API] Processing paper: {real_path}")
            
            # 读取文件内容
            paper_content = "\n".join(processor_manager.file_processor.load_document(real_path))
            print("[API] Document loaded, sending to WebSearchChain")
            
            # 调用处理链
            result = processor_manager.web_search_chain.process_paper(
                file_path=real_path,
                paper_content=paper_content,
                question=question
            )
        else:
            # 如果没有文件路径，只进行网络搜索
            print("[API] No file provided, performing web search only")
            try:
                response = processor_manager.web_search_chain.search_tool.run(question)
                result = {
                    "success": True,
                    "answer": response,
                    "context": "",  # 没有文档上下文
                    "search_results": response  # 搜索结果作为主要内容
                }
            except Exception as e:
                print(f"[API] Search error: {str(e)}")
                result = {
                    "success": False,
                    "error": str(e)
                }
            
        return JSONResponse(result)
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

@router.post("/recommend-papers")
async def recommend_papers(request: Request):
    """推荐相关论文"""
    try:
        data = await request.json()
        question = data.get("content", "")
        result = processor_manager.paper_search_chain.search(question)
        return JSONResponse(result)
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

@router.post("/chat")
async def chat(request: Request):
    """自定义聊天"""
    try:
        data = await request.json()
        message = data.get("content", "")
        
        if not message:
            return JSONResponse({
                "success": False,
                "error": "消息内容不能为空"
            })
            
        print(f"开始处理消息: {message}")  # 调试日志
        
        # 添加提示模板
        prompt = f"""请像一个专业的学术助手一样回答用户的问题。
        
用户问题: {message}

请提供专业、准确的回答。回答应该：
1. 使用清晰的学术语言
2. 提供具有参考价值的信息
3. 保持客观和准确性

回答:"""
        
        try:
            # 使用llm属性处理消息
            response = processor_manager.summary_chain.llm(prompt)
            print(f"模型返回结果: {response}")  # 调试日志
            
            if not response:
                raise ValueError("模型返回空响应")
                
            return JSONResponse({
                "success": True,
                "response": response
            })
            
        except Exception as model_error:
            print(f"模型处理错误: {str(model_error)}")  # 调试日志
            return JSONResponse({
                "success": False,
                "error": f"模型处理错误: {str(model_error)}"
            })
            
    except Exception as e:
        print(f"请求处理错误: {str(e)}")  # 调试日志
        return JSONResponse({
            "success": False,
            "error": f"请求处理错误: {str(e)}"
        })
