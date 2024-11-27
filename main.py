from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=4500, reload=True)
