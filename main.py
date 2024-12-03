from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
from datetime import datetime
import uuid

app = FastAPI()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="templates")

# 确保chat_history目录存在
CHAT_HISTORY_DIR = "chat_history"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

# 确保database目录存在
DATABASE_DIR = "database"
os.makedirs(DATABASE_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/save_chat")
async def save_chat(request: Request):
    try:
        data = await request.json()
        messages = data.get("messages", [])
        title = data.get("title", "新对话")
        chat_id = data.get("chat_id")

        if not chat_id:
            chat_id = str(uuid.uuid4())

        chat_data = {
            "id": chat_id,
            "title": title,
            "messages": messages,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 保存聊天记录
        with open(os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)

        return JSONResponse({
            "success": True,
            "chat_id": chat_id
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

@app.get("/get_chat_history")
async def get_chat_history():
    try:
        history = []
        for filename in os.listdir(CHAT_HISTORY_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(CHAT_HISTORY_DIR, filename), "r", encoding="utf-8") as f:
                    chat_data = json.load(f)
                    history.append({
                        "id": chat_data["id"],
                        "title": chat_data["title"],
                        "timestamp": chat_data["timestamp"]
                    })
        
        # 按时间戳降序排序
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_chat/{chat_id}")
async def get_chat(chat_id: str):
    try:
        chat_file = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
        if not os.path.exists(chat_file):
            return JSONResponse({
                "error": "Chat not found"
            })

        with open(chat_file, "r", encoding="utf-8") as f:
            chat_data = json.load(f)
            return chat_data
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        })

@app.delete("/delete_chat/{chat_id}")
async def delete_chat(chat_id: str):
    try:
        chat_file = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
        if not os.path.exists(chat_file):
            return JSONResponse({
                "error": "Chat not found"
            })

        os.remove(chat_file)
        return JSONResponse({
            "success": True
        })
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        })

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 生成唯一的文件名
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(DATABASE_DIR, f"{file_id}{file_extension}")

        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 返回文件URL
        return JSONResponse({
            "success": True,
            "fileUrl": f"/files/{file_id}{file_extension}",
            "fileName": file.filename
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

@app.get("/files/{file_name}")
async def get_file(file_name: str):
    file_path = os.path.join(DATABASE_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=3791, reload=True)
