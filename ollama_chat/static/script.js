// static/script.js
class OllamaChatApp {
    constructor() {
        this.isWaiting = false;
        this.currentModel = document.getElementById('model-select').value;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateWelcomeTime();
        this.checkServiceStatus();
        this.loadAvailableModels();
    }

    setupEventListeners() {
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');
        const clearBtn = document.getElementById('clear-btn');
        const modelSelect = document.getElementById('model-select');

        // 发送消息
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        // 按Enter发送
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 清空对话
        clearBtn.addEventListener('click', () => this.clearConversation());

        // 字符计数
        userInput.addEventListener('input', () => this.updateCharCount());

        // 模型切换
        modelSelect.addEventListener('change', (e) => {
            this.currentModel = e.target.value;
            this.addSystemMessage(`已切换到模型: ${this.currentModel}`);
        });
    }

    updateWelcomeTime() {
        const now = new Date();
        document.getElementById('welcome-time').textContent = this.formatTime(now);
    }

    updateCharCount() {
        const input = document.getElementById('user-input');
        const charCount = document.getElementById('char-count');
        charCount.textContent = `${input.value.length}/1000`;
    }

    async checkServiceStatus() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            const statusDot = document.getElementById('status-dot');
            const statusText = document.getElementById('status-text');
            
            if (data.status === 'healthy') {
                statusDot.className = 'status-dot healthy';
                statusText.textContent = 'Ollama服务正常';
            } else if (data.status === 'unhealthy') {
                statusDot.className = 'status-dot unhealthy';
                statusText.textContent = 'Ollama服务异常';
            } else {
                statusDot.className = 'status-dot';
                statusText.textContent = '无法连接Ollama';
            }
        } catch (error) {
            console.error('检查服务状态失败:', error);
        }
    }

    async loadAvailableModels() {
        try {
            const response = await fetch('/api/models');
            const data = await response.json();
            
            const modelSelect = document.getElementById('model-select');
            modelSelect.innerHTML = '';
            
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                option.selected = model === data.current_model;
                modelSelect.appendChild(option);
            });
            
            this.currentModel = data.current_model;
        } catch (error) {
            console.error('加载模型列表失败:', error);
        }
    }

    async sendMessage() {
        const userInput = document.getElementById('user-input');
        const message = userInput.value.trim();
        
        if (!message || this.isWaiting) return;

        // 添加用户消息到界面
        this.addMessage(message, 'user');
        userInput.value = '';
        this.updateCharCount();
        
        // 显示加载状态
        this.setLoading(true);
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    model: this.currentModel
                })
            });

            const data = await response.json();
            this.hideTypingIndicator();

            if (data.success) {
                // 添加AI回复到界面
                this.addMessage(data.reply, 'bot', data.timestamp, data.response_time, data.model);
            } else {
                this.addMessage(`错误: ${data.error}`, 'bot', data.timestamp);
            }

        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage(`网络错误: ${error.message}`, 'bot');
        } finally {
            this.setLoading(false);
        }
    }

    addMessage(content, sender, timestamp = null, responseTime = null, model = null) {
        const chatMessages = document.getElementById('chat-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (sender === 'bot') {
            let messageHTML = `<strong>AI助手:</strong> ${this.formatMessage(content)}`;
            
            // 添加元数据（响应时间、模型）
            if (responseTime || model) {
                messageHTML += `<div class="message-meta">`;
                if (responseTime) messageHTML += `响应: ${responseTime}`;
                if (model) messageHTML += ` | 模型: ${model}`;
                messageHTML += `</div>`;
            }
            
            messageContent.innerHTML = messageHTML;
        } else {
            messageContent.textContent = content;
        }
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = timestamp || this.getCurrentTime();
        
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(messageTime);
        chatMessages.appendChild(messageDiv);
        
        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    addSystemMessage(content) {
        const chatMessages = document.getElementById('chat-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';
        messageDiv.style.alignItems = 'center';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.style.backgroundColor = '#e9ecef';
        messageContent.style.color = '#495057';
        messageContent.style.fontStyle = 'italic';
        messageContent.textContent = content;
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chat-messages');
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message';
        typingDiv.id = 'typing-indicator';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'message-content';
        typingContent.innerHTML = `
            <strong>AI助手:</strong> 
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        typingDiv.appendChild(typingContent);
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    formatMessage(text) {
        // 简单的Markdown格式支持
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    getCurrentTime() {
        return this.formatTime(new Date());
    }

    formatTime(date) {
        return date.getHours().toString().padStart(2, '0') + ':' + 
               date.getMinutes().toString().padStart(2, '0');
    }

    setLoading(loading) {
        this.isWaiting = loading;
        const sendBtn = document.getElementById('send-btn');
        const userInput = document.getElementById('user-input');
        
        if (loading) {
            sendBtn.disabled = true;
            sendBtn.textContent = '思考中...';
            userInput.disabled = true;
        } else {
            sendBtn.disabled = false;
            sendBtn.textContent = '发送';
            userInput.disabled = false;
            userInput.focus();
        }
    }

    clearConversation() {
        if (!confirm('确定要清空对话历史吗？')) return;

        // 清空界面上的消息（保留欢迎消息）
        const chatMessages = document.getElementById('chat-messages');
        const welcomeMessage = chatMessages.querySelector('.bot-message');
        
        chatMessages.innerHTML = '';
        chatMessages.appendChild(welcomeMessage);
        
        this.updateWelcomeTime();
        this.addSystemMessage('对话历史已清空');
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new OllamaChatApp();
});