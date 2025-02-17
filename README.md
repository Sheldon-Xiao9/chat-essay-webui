# Chat-Essay-WebUI: 你的论文处理助手 🎓

一个基于 FastAPI 和现代前端技术构建的论文处理助手，帮助你更好地阅读和理解学术论文。

## 功能特点 ✨

- 💬 智能对话：通过自然语言与论文内容进行交互
- 📚 论文处理：支持上传和处理学术论文
- 🌓 动态主题：支持浅色/深色主题切换
- 💾 会话历史：自动保存和管理聊天记录
- 🎨 现代界面：简洁优雅的用户界面设计

## 技术栈 🛠️

### 后端
- FastAPI：高性能的 Python Web 框架
- Uvicorn：轻量级 ASGI 服务器
- Python-multipart：处理文件上传
- JSON：用于数据存储

### 前端
- HTML5 + CSS3：现代网页布局和样式
- JavaScript：原生 JS 实现交互功能
- Remix Icon：优雅的图标库
- Google Fonts：精美的字体支持

## 快速开始 🚀

### 环境要求
- Python 3.11
- pip（Python 包管理器）

### 安装步骤

1. 克隆仓库
```bash
git clone [repository-url]
cd chat-essay
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动服务器
```bash
python main.py
```

4. 访问应用
打开浏览器，访问 http://localhost:3791

## 项目结构 📁

```
chat-essay/
├── main.py              # FastAPI 应用主文件
├── requirements.txt     # Python 依赖列表
├── static/             # 静态资源目录
│   ├── images/         # 图片资源
│   ├── script.js       # JavaScript 文件
│   └── styles.css      # CSS 样式文件
├── templates/          # 模板目录
│   └── index.html      # 主页面模板
└── chat_history/       # 聊天历史记录存储目录
```

## 使用说明 📖

1. 开始新对话
   - 点击侧边栏的"+"按钮
   - 在输入框中输入问题或上传论文

2. 上传论文
   - 点击输入框左侧的上传按钮
   - 选择 PDF 或 Word 格式的论文文件

3. 查看历史记录
   - 打开侧边栏查看历史对话
   - 点击任意历史记录可恢复对话

4. 切换主题
   - 点击右上角的主题切换按钮
   - 在浅色和深色主题之间切换


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
