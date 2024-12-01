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

// 全局变量
let currentChatId = null;

document.addEventListener('DOMContentLoaded', function() {
    const navButtons = document.querySelectorAll('.nav-button-welcome');
    const navSlider = document.querySelector('.nav-slider');

    // 移动滑块的函数
    function moveSlider(index) {
        const button = navButtons[index];
        const buttonWidth = button.offsetWidth;
        const buttonMarginLeft = 2;
        const buttonMarginRight = 10;
        const totalMargin = buttonMarginLeft + buttonMarginRight;
        const offset = index * (buttonWidth + totalMargin);
        navSlider.style.transform = `translateX(${offset}px)`;
    }

    // 切换按钮激活状态的函数
    function setActiveButton(index) {
        navButtons.forEach(btn => btn.removeAttribute('data-active'));
        navButtons[index].setAttribute('data-active', 'true');
        moveSlider(index);
    }

    // 默认激活第一个按钮
    if (navButtons.length > 0) {
        setActiveButton(0);
    }

    // 导航按钮点击事件
    navButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            setActiveButton(index);
        });
    });

    // 侧边栏切换
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        mainContent.classList.toggle('sidebar-open');

        if (sidebar.classList.contains('open')) {
            loadChatHistory();
        } 
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
            chatInputContainer.classList.remove('hidden');
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

        // 保存聊天记录（无论是用户消息还是助手消息）
        await saveCurrentChat();
    }

    // 保存当前聊天记录
    async function saveCurrentChat() {
        const messages = [];
        messagesContainer.querySelectorAll('.message').forEach(msgEl => {
            messages.push({
                role: msgEl.classList.contains('user') ? 'user' : 'assistant',
                content: msgEl.querySelector('.message-content').textContent
            });
        });
        
        if (messages.length === 0) return;
        
        const firstUserMessage = messages.find(msg => msg.role === 'user')?.content || '新对话';
        const title = firstUserMessage.length > 20 ? firstUserMessage.substring(0, 20) + '...' : firstUserMessage;
        
        try {
            const response = await fetch('/save_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    chat_id: currentChatId,
                    messages: messages,
                    title: title
                })
            });
            
            const data = await response.json();
            if (data.success) {
                currentChatId = data.chat_id;
                await loadChatHistory(); // 刷新历史记录
            }
        } catch (error) {
            console.error('Error saving chat:', error);
        }
    }

    // 加载聊天历史
    async function loadChatHistory() {
        try {
            const response = await fetch('/get_chat_history');
            const history = await response.json();
            
            const historyContainer = document.querySelector('.chat-history');
            historyContainer.innerHTML = '';
            
            history.forEach(chat => {
                const historyItem = document.createElement('div');
                historyItem.className = 'chat-history-item';
                historyItem.setAttribute('data-chat-id', chat.id);
                historyItem.innerHTML = `
                    <i class="ri-chat-history-line"></i>
                    <span>${chat.title}</span>
                `;
                historyItem.addEventListener('click', () => loadChat(chat.id));
                historyContainer.appendChild(historyItem);
            });
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    // 加载特定的聊天记录
    async function loadChat(chatId) {
        try {
            const response = await fetch(`/get_chat/${chatId}`);
            const chatData = await response.json();
            
            if (chatData.error) {
                console.error('Error loading chat:', chatData.error);
                return;
            }
            
            // 切换到聊天模式
            switchToChatMode();
            
            // 清空当前消息
            messagesContainer.innerHTML = '';
            
            // 加载消息
            for (const msg of chatData.messages) {
                const messageElement = createMessageElement(msg.content, msg.role === 'user');
                messagesContainer.appendChild(messageElement);
            }
            
            // 更新当前聊天ID
            currentChatId = chatId;
            
            // 在移动端自动关闭侧边栏
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('open');
                mainContent.classList.remove('sidebar-open');
            }
        } catch (error) {
            console.error('Error loading chat:', error);
        }
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

    // 重置UI到初始状态的函数
    function resetToInitialState() {
        // 重置当前聊天ID
        currentChatId = null;
        
        // 获取所有需要操作的元素
        const welcomeContainer = document.getElementById('welcome-container');
        const messages = document.getElementById('messages');
        const chatInputContainer = document.getElementById('chat-input-container');
        const chatBottom = document.querySelector('.chat-bottom');

        // 显示欢迎界面
        welcomeContainer.classList.remove('hidden');
        
        // 隐藏消息区域和底部输入框
        messages.classList.add('hidden');
        messages.classList.remove('visible');
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
    // homeButton.addEventListener('click', function() {
    //     // 隐藏聊天区域，显示欢迎界面
    //     document.querySelector('.chat-area').style.display = 'none';
    //     document.getElementById('welcome-container').style.display = 'flex';
        
    //     // 清空聊天记录
    //     document.getElementById('chat-messages').innerHTML = '';
        
    //     // 关闭侧边栏
    //     document.getElementById('sidebar').classList.remove('open');
    //     document.querySelector('.main-content').classList.remove('sidebar-open');
        
    //     // 重置输入框
    //     document.querySelector('#initial-input .chat-input').value = '';
    //     document.querySelector('.chat-input-container .input-wrapper .chat-input').value = '';
        
    //     // 隐藏底部输入框
    //     document.querySelector('.chat-input-container').style.display = 'none';
    // });

    // 侧边栏按钮点击事件
    document.querySelectorAll('.sidebar-action-btn').forEach(button => {
        button.addEventListener('click', () => {
            // 清除欢迎界面，显示聊天界面
            resetToInitialState();

            const action = button.querySelector('i').nextSibling.textContent.trim();
            
            // 添加到历史记录
            // addHistoryItem(action);
            
            // 根据不同的按钮设置对应的导航状态
            switch (action) {
                case '帮你写摘要...':
                    setActiveButton(1);
                    break;
                case '带你读论文...':
                    setActiveButton(2);
                    break;
                case '给你推文献...':
                    setActiveButton(3);
                    break;
                case '自定义聊天':
                    setActiveButton(0);
                    break;
                default:
                    setActiveButton(0);
            }
        });
    });
});
