# app.py
from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime
import time
import base64
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

class WorkingAIGenerator:
    def __init__(self):
        # 使用已知可工作的模型
        self.available_models = [
            {
                "name": "Stable Diffusion XL",
                "id": "stabilityai/stable-diffusion-xl-base-1.0",
                "value": 0
            },
            {
                "name": "OpenJourney V4", 
                "id": "prompthero/openjourney-v4",
                "value": 1
            },
            {
                "name": "DreamShaper",
                "id": "lykon/dreamshaper-8",
                "value": 2
            }
        ]
    
    def get_models(self):
        return self.available_models
    
    def generate_image(self, prompt, model_index=0):
        """使用可工作的模型生成图片"""
        if not HUGGINGFACE_API_KEY:
            return None, "请设置HUGGINGFACE_API_KEY环境变量"
        
        model_info = self.available_models[model_index]
        model_id = model_info["id"]
        api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "options": {
                "wait_for_model": True,
                "use_cache": True
            },
            "parameters": {
                "num_inference_steps": 20,
                "guidance_scale": 7.5
            }
        }
        
        try:
            print(f"使用模型: {model_info['name']} ({model_id})")
            print(f"提示词: {prompt}")
            
            start_time = time.time()
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            response_time = time.time() - start_time
            print(f"⏱响应时间: {response_time:.2f}s")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 成功生成图片
                image = Image.open(BytesIO(response.content))
                
                # 转换为base64
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # 保存文件 - 确保路径正确
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"static/generated/generated_{timestamp}.png"
                os.makedirs(os.path.dirname(filename), exist_ok=True)  # 确保目录存在
                image.save(filename)
                
                return f"data:image/png;base64,{img_str}", f"生成成功! 耗时: {response_time:.1f}s"
            
            elif response.status_code == 503:
                # 模型正在加载
                try:
                    error_info = response.json()
                    wait_time = error_info.get("estimated_time", 30)
                    return None, f"模型正在加载，请等待约 {wait_time:.0f} 秒后重试"
                except:
                    return None, "模型正在加载，请稍后重试"
            
            elif response.status_code == 404:
                return None, f"模型端点不存在: {model_id}"
            
            else:
                error_msg = f"API错误: {response.status_code}"
                try:
                    error_info = response.json()
                    if "error" in error_info:
                        error_msg += f" - {error_info['error']}"
                except:
                    error_msg += f" - {response.text[:100]}"
                return None, error_msg
                
        except requests.exceptions.Timeout:
            return None, "请求超时，请重试"
        except Exception as e:
            return None, f"生成失败: {str(e)}"

# 初始化生成器
ai_generator = WorkingAIGenerator()

@app.route('/')
def index():
    models = ai_generator.get_models()
    return render_template('index.html', models=models)

@app.route('/api/generate_image', methods=['POST'])
def generate_image_api():
    data = request.get_json()
    prompt = data.get('prompt', '')
    model_index = data.get('model_index', 0)
    
    if not prompt.strip():
        return jsonify({
            "success": False,
            "error": "提示词不能为空"
        })
    
    image_data, message = ai_generator.generate_image(prompt, model_index)
    
    if image_data:
        return jsonify({
            "success": True,
            "image_data": image_data,
            "message": message,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    else:
        return jsonify({
            "success": False,
            "error": message
        })

if __name__ == '__main__':
    print("启动AI图片生成器...")
    print("项目路径:", os.getcwd())
    print("访问 http://localhost:5000")
    
    # 创建必要的文件夹
    os.makedirs("static/generated", exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)