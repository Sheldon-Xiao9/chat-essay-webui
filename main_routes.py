from fastapi import APIRouter, HTTPException, File, UploadFile, Request
from fastapi.responses import JSONResponse
import os
import uuid
from typing import Dict, Any
from chains.rag_chains.summary_chain import SummaryChain
from chains.api_chains.web_search import WebSearchChain
from chains.api_chains.paper_search import PaperSearchChain
from utils.file_processor import FileProcessor

router = APIRouter()

# 初始化处理器
file_processor = FileProcessor()
summary_chain = SummaryChain()
web_search_chain = WebSearchChain()
paper_search_chain = PaperSearchChain()

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
            result = summary_chain.process_file(real_path, query)
        else:
            # 如果没有文件路径，直接处理文本查询
            response = summary_chain.llm(query)
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
            paper_content = "\n".join(file_processor.load_document(real_path))
            result = web_search_chain.process_paper(paper_content, question)
        else:
            # 如果没有文件路径，直接回答问题
            response = web_search_chain.search_tool.run(question)
            result = {
                "success": True,
                "answer": response
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
        result = paper_search_chain.search(question)
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
        response = summary_chain.llm(message)
        
        return JSONResponse({
            "success": True,
            "response": response
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })
