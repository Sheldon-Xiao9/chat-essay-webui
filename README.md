# Chat-Essay-WebUI: 你的论文处理助手 🎓

一个基于 FastAPI 和 LangChain 构建的智能论文处理助手，帮助你更好地阅读、理解和分析学术论文。

## 功能特点 ✨

- 💬 智能对话：通过自然语言与论文内容进行交互
- 📝 论文总结：自动生成论文摘要和关键点提取
- 🔍 文献推荐：基于当前论文推荐相关研究文献
- 🌐 网络搜索：集成网络搜索功能，补充论文相关信息
- 📚 本地处理：支持 PDF 格式的论文处理
- 🌓 动态主题：支持浅色/深色主题切换
- 💾 会话历史：自动保存和管理聊天记录
- 🎨 现代界面：简洁优雅的用户界面设计

## 技术栈 🛠️

### 后端
- FastAPI：高性能的 Python Web 框架
- LangChain：强大的 AI 应用开发框架
- PyPDF & python-docx：文档处理工具
- FAISS：高效向量存储和检索
- Transformers：AI 模型加载和推理
- Uvicorn：轻量级 ASGI 服务器

### 前端
- HTML5 + CSS3：现代网页布局和样式
- JavaScript：原生 JS 实现交互功能
- Remix Icon：优雅的图标库
- Google Fonts：精美的字体支持

## 快速开始 🚀

### 环境要求
- Python 3.11+
- pip（Python 包管理器）
- 8GB+ RAM（推荐）

### 安装步骤

1. 克隆仓库
```bash
git clone [repository-url]
cd chat-essay-webui
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 创建模型目录
- Linux/MacOS请使用如下命令
```bash
sh utils/create_model_dirs.sh
```
- Windows请使用如下命令
```bash
utils/create_model_dirs.bat
```

4. 下载模型文件并放入相应目录
- 用于用户交互的模型文件放在 `models/chat` 目录下
- 用于向量化处理的模型文件放在 `models/embedded` 目录下

5. 启动服务器
```bash
python main.py
```

6. 访问应用
打开浏览器，访问 http://localhost:3791

## 项目结构 📁

```
chat-essay-webui/
├── main.py              # FastAPI 应用主文件
├── main_routes.py       # API 路由和处理器
├── requirements.txt     # Python 依赖列表
├── chains/             # LangChain 处理链
│   ├── api_chains/     # API 相关处理链
│   │   ├── paper_search.py    # 论文搜索链
│   │   └── web_search.py      # 网络搜索链
│   └── rag_chains/     # RAG 处理链
│       └── summary_chain.py    # 摘要生成链
├── utils/              # 工具函数
│   ├── create_model_dirs.bat   # Windows 模型目录创建脚本
│   ├── create_model_dirs.sh    # Linux 模型目录创建脚本
│   ├── file_processor.py       # 文件处理工具
│   ├── model_loader.py         # 模型加载工具
│   └── vectorizer.py           # 向量化工具
├── static/             # 静态资源目录
│   ├── images/         # 图片资源
│   ├── script.js       # 主要 JavaScript 文件
│   ├── settings.js     # 设置相关 JavaScript
│   └── styles.css      # CSS 样式文件
├── templates/          # 模板目录
│   └── index.html      # 主页面模板
├── chat_history/       # 聊天历史记录存储
└── database/           # 上传文件存储目录
```

## 核心功能 📖

### 1. 论文处理和分析
- 支持上传 PDF 格式的论文
- 自动提取和分析论文内容
- 生成论文摘要和关键点
- 智能问答和内容解析

### 2. 智能搜索和推荐
- 基于论文内容进行相关文献推荐
- 集成网络搜索补充相关信息
- 智能匹配相关研究资料

### 3. 会话管理
- 自动保存对话历史
- 支持恢复历史会话
- 文件关联记录

### 4. 用户界面
- 响应式设计
- 深色/浅色主题切换
- 直观的文件上传和管理
- 流畅的对话交互体验

## 使用说明 🔄

1. 论文处理
   - 点击上传按钮选择 PDF 格式论文
   - 等待系统完成文件处理
   - 通过对话框与助手进行交互

2. 智能对话
   - 可以询问论文相关的具体问题
   - 请求生成论文摘要
   - 寻找相关研究文献

3. 历史管理
   - 所有对话自动保存
   - 通过侧边栏访问历史记录
   - 可随时恢复之前的对话

## 贡献指南 🤝

欢迎提交 Pull Request 或 Issue！

1. Fork 本仓库
2. 创建新分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

## 许可证 📄

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式 📧

如有问题或建议，欢迎联系：
- 项目主页：[chat-essay-webui](https://github.com/Sheldon-Xiao9/chat-essay-webui)
- 电子邮件：[Sheldon Xiao](mailto:sheldonhomes9@hotmail.com)
