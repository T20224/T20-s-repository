# app.py
from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime
import time

app = Flask(__name__)

# Ollama API配置
OLLAMA_BASE_URL = "http://localhost:11434"  # 默认Ollama地址

class OllamaChatAgent:
    def __init__(self):
        self.available_models = self.get_available_models()
        self.current_model = "deepseek-r1:7b"  # 默认模型
        
    def get_available_models(self):
        """获取可用的Ollama模型"""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                models_data = response.json()
                return [model["name"] for model in models_data.get("models", [])]
            else:
                print(f"无法获取模型列表: {response.status_code}")
                return ["llama2"]  # 默认回退
        except Exception as e:
            print(f"获取模型时出错: {e}")
            return ["llama2"]  # 默认回退
    
    def chat(self, message, conversation_history=None, model=None):
        """与Ollama模型对话"""
        if model is None:
            model = self.current_model
            
        # 构建对话历史
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        
        # 添加当前消息
        messages.append({"role": "user", "content": message})
        
        try:
            # 调用Ollama API
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            start_time = time.time()
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload,
                timeout=60  # 60秒超时
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                assistant_reply = result["message"]["content"]
                
                # 更新对话历史
                if conversation_history is not None:
                    conversation_history.append({"role": "user", "content": message})
                    conversation_history.append({"role": "assistant", "content": assistant_reply})
                
                return {
                    "success": True,
                    "reply": assistant_reply,
                    "response_time": f"{response_time:.2f}s",
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "model": model
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama API错误: {response.status_code} - {response.text}",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "无法连接到Ollama服务。请确保Ollama正在运行。",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"请求失败: {str(e)}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
    
    def get_models(self):
        """获取可用模型列表"""
        return self.available_models
    
    def set_model(self, model_name):
        """设置当前模型"""
        if model_name in self.available_models:
            self.current_model = model_name
            return True
        return False

# 初始化聊天代理
agent = OllamaChatAgent()

@app.route('/')
def index():
    return render_template('index.html', models=agent.get_models())

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    user_message = data.get('message', '')
    model = data.get('model', agent.current_model)
    
    if not user_message.strip():
        return jsonify({
            "success": False,
            "error": "消息不能为空"
        })
    
    # 设置模型
    if model != agent.current_model:
        agent.set_model(model)
    
    result = agent.chat(user_message)
    return jsonify(result)

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取可用模型列表"""
    return jsonify({
        "models": agent.get_models(),
        "current_model": agent.current_model
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """检查Ollama服务状态"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return jsonify({
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "ollama_status": response.status_code
        })
    except:
        return jsonify({"status": "unreachable"})

if __name__ == '__main__':
    print("🚀 启动Ollama对话网页...")
    print(f"📚 可用模型: {', '.join(agent.get_models())}")
    print("🌐 访问 http://localhost:5000 开始聊天")
    app.run(debug=True, host='0.0.0.0', port=5000)