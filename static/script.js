// DOM 元素
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');
const mainContent = document.querySelector('.main-content');
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');
const fileUpload = document.getElementById('file-upload');
const fileUploadBottom = document.getElementById('file-upload-bottom');
const chatInputs = document.querySelectorAll('.chat-input');
const sendButtons = document.querySelectorAll('.send-button');
const messagesContainer = document.getElementById('messages');
const welcomeContainer = document.getElementById('welcome-container');
const chatInputContainer = document.getElementById('chat-input-container');
const sidebarClose = document.querySelector('.sidebar-close');
const homeButton = document.querySelector('.home-button');
const newChatButton = document.querySelector('.new-chat-button');

document.addEventListener('DOMContentLoaded', function() {
    // 侧边栏切换
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        mainContent.classList.toggle('sidebar-open');
    });

    // 主题切换
    let isDarkMode = false;

    themeToggle.addEventListener('click', () => {
        isDarkMode = !isDarkMode;
        document.body.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
        themeIcon.className = isDarkMode ? 'ri-moon-line' : 'ri-sun-line';
    });

    // 切换到聊天模式
    function switchToChatMode() {
        welcomeContainer.classList.add('hidden');
        setTimeout(() => {
            chatInputContainer.classList.add('visible');
            messagesContainer.classList.remove('hidden');
            messagesContainer.classList.add('visible');
        }, 300);
    }

    // 创建消息元素
    function createMessageElement(content, isUser = false, isLoading = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;

        if (!isUser) {
            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'message-avatar';
            const avatarImg = document.createElement('img');
            avatarImg.src = '/static/images/assist_avatar.svg';
            avatarImg.alt = 'Assistant Avatar';
            avatarDiv.appendChild(avatarImg);
            messageDiv.appendChild(avatarDiv);
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (isLoading) {
            contentDiv.innerHTML = `
                <div class="loading-dots">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
            `;
        } else {
            contentDiv.textContent = content;
        }
        
        messageDiv.appendChild(contentDiv);
        return messageDiv;
    }

    // 模拟打字效果
    async function typeMessage(element, text, delay = 50) {
        const contentDiv = element.querySelector('.message-content');
        contentDiv.textContent = '';
        contentDiv.classList.add('typing');
        
        for (let char of text) {
            contentDiv.textContent += char;
            await new Promise(resolve => setTimeout(resolve, delay));
        }
        
        contentDiv.classList.remove('typing');
    }

    // 添加消息到聊天区域
    async function addMessage(content, isUser = false) {
        if (messagesContainer.children.length === 0) {
            switchToChatMode();
        }

        if (!isUser) {
            // 首先添加加载动画
            const loadingMessage = createMessageElement('', false, true);
            messagesContainer.appendChild(loadingMessage);
            loadingMessage.scrollIntoView({ behavior: 'smooth', block: 'end' });

            // 模拟接收服务器响应
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // 替换加载动画为实际消息
            const messageElement = createMessageElement(content, false);
            messagesContainer.replaceChild(messageElement, loadingMessage);
            
            // 应用打字机效果
            await typeMessage(messageElement, content);
        } else {
            const messageElement = createMessageElement(content, true);
            messagesContainer.appendChild(messageElement);
        }

        // 滚动到最新消息
        messagesContainer.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }

    // 处理文件上传
    async function handleFileUpload(file) {
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                console.log('文件上传成功:', result);
                addMessage(`已上传文件: ${file.name}`, true);
                // 模拟助手回复
                setTimeout(() => {
                    addMessage(`我已经收到文件 ${file.name}，正在分析中...`);
                }, 1000);
            } else {
                console.error('文件上传失败');
                addMessage('文件上传失败，请重试。', true);
            }
        } catch (error) {
            console.error('上传过程中发生错误:', error);
            addMessage('上传过程中发生错误，请重试。', true);
        }
    }

    // 文件上传处理
    fileUpload.addEventListener('change', (e) => handleFileUpload(e.target.files[0]));
    fileUploadBottom.addEventListener('change', (e) => handleFileUpload(e.target.files[0]));

    // 发送消息
    async function sendMessage(input) {
        const message = input.value.trim();
        if (!message) return;

        // 添加用户消息
        await addMessage(message, true);
        input.value = '';

        // 如果是第一条消息，添加到历史记录
        if (messagesContainer.children.length === 1) {
            const title = message.length > 20 ? message.substring(0, 20) + '...' : message;
            addHistoryItem(title);
        }

        // 模拟助手回复
        await addMessage('我已经收到你的问题，让我思考一下...');
    }

    // 为所有输入框和发送按钮添加事件监听
    chatInputs.forEach((input, index) => {
        const sendButton = sendButtons[index];
        
        // 发送按钮点击事件
        sendButton.addEventListener('click', () => sendMessage(input));

        // 按回车发送消息
        input.addEventListener('keypress', async (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                await sendMessage(input);
            }
        });
    });

    // 添加历史记录项
    function addHistoryItem(title) {
        const historyContainer = document.querySelector('.chat-history');
        const historyItem = document.createElement('div');
        historyItem.className = 'chat-history-item';
        historyItem.innerHTML = `
            <i class="ri-chat-history-line"></i>
            <span>${title}</span>
        `;
        historyContainer.prepend(historyItem);
    }

    // 重置UI到初始状态的函数
    function resetToInitialState() {
        // 获取所有需要操作的元素
        const welcomeContainer = document.getElementById('welcome-container');
        const messages = document.getElementById('messages');
        const chatInputContainer = document.getElementById('chat-input-container');
        const chatBottom = document.querySelector('.chat-bottom');

        // 显示欢迎界面
        welcomeContainer.classList.remove('hidden');
        
        // 隐藏消息区域和底部输入框
        messages.classList.add('hidden');
        chatInputContainer.classList.remove('visible');
        chatInputContainer.classList.add('hidden');
        if (chatBottom) {
            chatBottom.style.display = 'none';
        }
        
        // 清空消息区域
        messages.innerHTML = '';
        
        // 重置所有输入框的值
        const inputs = document.querySelectorAll('.chat-input');
        inputs.forEach(input => input.value = '');
        
        // 关闭侧边栏
        sidebar.classList.remove('open');
        mainContent.classList.remove('sidebar-open');
    }

    // 新会话按钮点击事件
    newChatButton.addEventListener('click', resetToInitialState);

    // 侧边栏关闭
    sidebarClose.addEventListener('click', () => {
        sidebar.classList.remove('open');
        mainContent.classList.remove('sidebar-open');
    });

    // 首页按钮点击事件
    homeButton.addEventListener('click', function() {
        // 隐藏聊天区域，显示欢迎界面
        document.querySelector('.chat-area').style.display = 'none';
        document.getElementById('welcome-container').style.display = 'flex';
        
        // 清空聊天记录
        document.getElementById('chat-messages').innerHTML = '';
        
        // 关闭侧边栏
        document.getElementById('sidebar').classList.remove('open');
        document.querySelector('.main-content').classList.remove('sidebar-open');
        
        // 重置输入框
        document.querySelector('#initial-input .chat-input').value = '';
        document.querySelector('.chat-input-container .input-wrapper .chat-input').value = '';
        
        // 隐藏底部输入框
        document.querySelector('.chat-input-container').style.display = 'none';
    });

    // 侧边栏按钮点击事件
    document.querySelectorAll('.sidebar-action-btn').forEach(button => {
        button.addEventListener('click', () => {
            const action = button.textContent.trim();
            // 清除欢迎界面，显示聊天界面
            document.getElementById('welcome-container').classList.add('hidden');
            document.getElementById('messages').classList.remove('hidden');
            document.getElementById('chat-input-container').classList.remove('hidden');
            
            // 添加到历史记录
            addHistoryItem(action);
            
            // 这里可以添加不同按钮的具体行为
        });
    });
});
