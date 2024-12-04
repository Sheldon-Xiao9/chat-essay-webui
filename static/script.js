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
const splitMessagesContainer = document.getElementById('split-messages');
const welcomeContainer = document.getElementById('welcome-container');
const chatInputContainer = document.getElementById('chat-input-container');
const sidebarClose = document.querySelector('.sidebar-close');
const homeButton = document.querySelector('.home-button');
const newChatButton = document.querySelector('.new-chat-button');

// 全局变量
let currentChatId = null;
let currentPdfPath = null; // 添加PDF路径变量

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

        // 切换输入界面
        const chatInputWrapper = document.querySelector('.chat-input-wrapper');
        
        // 根据不同的按钮显示不同的输入界面
        if (index === 0 || index === 3) { // 开始聊天或推荐文献
            chatInputWrapper.classList.remove('upload-mode');
        } else { // 摘要生成或阅读论文
            chatInputWrapper.classList.add('upload-mode');
        }
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
        // 确定当前活动的消息容器
        const isSplitView = !document.getElementById('split-view').classList.contains('hidden');
        const activeMessages = isSplitView ? splitMessagesContainer : messagesContainer;

        // 处理界面切换
        if (!isSplitView && messagesContainer.children.length === 0) {
            switchToChatMode();
        } else if (isSplitView) {
            document.getElementById('split-view').classList.remove('hidden');
            chatInputContainer.classList.remove('hidden');
            chatInputContainer.classList.add('visible');
            splitMessagesContainer.classList.remove('hidden');
            splitMessagesContainer.classList.add('visible');
        }

        if (!isUser) {
            // 首先添加加载动画
            const loadingMessage = createMessageElement('', false, true);
            activeMessages.appendChild(loadingMessage);
            loadingMessage.scrollIntoView({ behavior: 'smooth', block: 'end' });

            // 模拟接收服务器响应
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // 替换加载动画为实际消息
            const messageElement = createMessageElement(content, false);
            activeMessages.replaceChild(messageElement, loadingMessage);
            
            // 应用打字机效果
            await typeMessage(messageElement, content);
        } else {
            const messageElement = createMessageElement(content, true);
            activeMessages.appendChild(messageElement);
        }

        // 确保消息容器可见
        if (isSplitView) {
            splitMessagesContainer.style.display = 'flex';
            splitMessagesContainer.style.flexDirection = 'column';
        }

        // 滚动到最新消息
        activeMessages.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'end' });

        // 保存聊天记录
        await saveCurrentChat();
    }

    // 保存当前聊天记录
    async function saveCurrentChat() {
        const messages = [];

        // 根据聊天模式选择正确的消息容器
        const activeMessages = !document.getElementById('split-view').classList.contains('hidden') ? 
        document.getElementById('split-messages') : 
        document.getElementById('messages');

        activeMessages.querySelectorAll('.message').forEach(msgEl => {
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
                    title: title,
                    file_path: currentPdfPath
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
                
                const icon = document.createElement('i');
                icon.className = 'ri-chat-history-line';
                
                const span = document.createElement('span');
                span.textContent = chat.title;
                
                const deleteButton = document.createElement('button');
                deleteButton.className = 'delete-button';
                deleteButton.title = '删除';
                deleteButton.innerHTML = '<i class="ri-delete-bin-5-line"></i>';
                
                // 为删除按钮添加点击事件
                deleteButton.addEventListener('click', async (e) => {
                    e.stopPropagation(); // 阻止事件冒泡
                    await deleteChat(chat.id);
                });
                
                // 为历史记录项添加点击事件
                historyItem.addEventListener('click', () => loadChat(chat.id));
                
                historyItem.appendChild(icon);
                historyItem.appendChild(span);
                historyItem.appendChild(deleteButton);
                historyContainer.appendChild(historyItem);
            });
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    // 加载特定的聊天记录
    async function loadChat(chatId) {
        resetToInitialState();
        
        try {
            const response = await fetch(`/get_chat/${chatId}`);
            const chatData = await response.json();
            
            if (chatData.error) {
                console.error('Error loading chat:', chatData.error);
                return;
            }
            
            // 切换到聊天模式
            if (!chatData.file_path) {
                switchToChatMode();
                const activeMessages = document.getElementById('messages');
                // 清空当前消息
                activeMessages.innerHTML = '';
                
                // 加载消息
                for (const msg of chatData.messages) {
                    const messageElement = createMessageElement(msg.content, msg.role === 'user');
                    activeMessages.appendChild(messageElement);
                }
            } else {
                document.getElementById('welcome-container').classList.add('hidden');
                document.getElementById('split-view').classList.remove('hidden');
                document.getElementById('pdf-viewer').innerHTML = `<iframe src="${chatData.file_path}"></iframe>`;
                document.getElementById('chat-input-container').classList.remove('hidden');
                
                const activeMessages = document.getElementById('split-messages');
                activeMessages.classList.remove('hidden'); 
                activeMessages.classList.add('visible'); // 添加visible类使消息可见
                // 清空当前消息
                activeMessages.innerHTML = '';
                
                // 加载消息
                for (const msg of chatData.messages) {
                    const messageElement = createMessageElement(msg.content, msg.role === 'user');
                    activeMessages.appendChild(messageElement);
                }
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

    // 删除特定的聊天记录
    async function deleteChat(chatId) {
        try {
            const response = await fetch(`/delete_chat/${chatId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            if (!response.ok) {
                console.error('Failed to delete chat:', data.error);
            }
            
            // 无论删除是否成功，都刷新历史记录
            await loadChatHistory();
        } catch (error) {
            console.error('Error deleting chat:', error);
            // 即使发生错误也尝试刷新历史记录
            await loadChatHistory();
        }
    }

    // 处理文件上传
    async function handleFileUpload(file) {
        if (!file) return;

        const loadingContainer = document.getElementById('loading-container');
        const progressBar = loadingContainer.querySelector('.progress-bar');
        const progressText = loadingContainer.querySelector('.progress-text');
        const welcomeContainer = document.getElementById('welcome-container');
        const splitView = document.getElementById('split-view');
        const chatInputContainer = document.getElementById('chat-input-container');

        // 显示loading界面
        loadingContainer.classList.remove('hidden');

        // 创建FormData对象
        const formData = new FormData();
        formData.append('file', file);

        try {
            // 上传文件
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    progressBar.style.width = `${percentCompleted}%`;
                    progressText.textContent = `${percentCompleted}%`;
                }
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();

            // 隐藏loading和欢迎界面
            loadingContainer.classList.add('hidden');
            welcomeContainer.classList.add('hidden');

            // 显示分栏界面
            splitView.classList.remove('hidden');
            chatInputContainer.classList.remove('hidden');

            // 加载PDF文件到viewer
            const pdfViewer = document.getElementById('pdf-viewer');
            if (file.type === 'application/pdf') {
                const fileUrl = data.fileUrl;
                pdfViewer.innerHTML = `<iframe src="${fileUrl}" width="100%" height="100%" frameborder="0"></iframe>`;
                currentPdfPath = fileUrl; // 保存PDF文件路径
                await saveCurrentChat();
            } else {
                // 如果不是PDF，显示文件名和类型
                pdfViewer.innerHTML = `
                    <div class="file-info">
                        <h3>${file.name}</h3>
                        <p>文件类型: ${file.type}</p>
                    </div>
                `;
            }

            addMessage('文件上传成功，您需要做什么？');

        } catch (error) {
            console.error('Error uploading file:', error);
            loadingContainer.classList.add('hidden');
            alert('文件上传失败，请重试');
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
        const splitView = document.getElementById('split-view');
        const pdfViewer = document.getElementById('pdf-viewer');
        const loadingContainer = document.getElementById('loading-container');
        const chatBottom = document.querySelector('.chat-bottom');

        // 显示欢迎界面
        welcomeContainer.classList.remove('hidden');
        // 清空所有消息容器
        messagesContainer.innerHTML = '';
        splitMessagesContainer.innerHTML = '';

        // 重置所有输入框的值
        const inputs = document.querySelectorAll('.chat-input');
        inputs.forEach(input => input.value = '');

        // 重置文件上传
        const fileUploads = document.querySelectorAll('input[type="file"]');
        fileUploads.forEach(input => input.value = '');

        // 重置PDF查看器
        if (pdfViewer) {
            pdfViewer.innerHTML = '';
            currentPdfPath = null; // 重置PDF路径
        }

        // 隐藏所有非欢迎界面元素
        loadingContainer?.classList.add('hidden');
        splitView?.classList.add('hidden');
        chatInputContainer.classList.remove('visible');
        chatInputContainer.classList.add('hidden');
        messagesContainer.classList.add('hidden');
        messagesContainer.classList.remove('visible');
        if (chatBottom) {
            chatBottom.style.display = 'none';
        }

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
