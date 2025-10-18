# detailed_diagnosis.py
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

def detailed_diagnosis():
    print("🔍 开始详细网络诊断...")
    print("=" * 50)
    
    # 1. 检查API密钥
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    if not api_key:
        print("❌ 错误: 未找到HUGGINGFACE_API_KEY")
        return False
    
    print(f"✅ API密钥存在: {api_key[:10]}...")
    
    # 2. 测试基本网络连接
    test_urls = [
        ("百度", "https://www.baidu.com"),
        ("Google", "https://www.google.com"),
        ("Hugging Face", "https://huggingface.co"),
    ]
    
    for name, url in test_urls:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            print(f"✅ {name}连接正常 - 响应时间: {response_time:.2f}s - 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}连接失败: {e}")
    
    # 3. 测试Hugging Face API状态
    print("\n🔧 测试Hugging Face API端点...")
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # 测试不同的API端点
    api_endpoints = [
        ("用户信息", "https://huggingface.co/api/whoami-v2"),
        ("模型列表", "https://huggingface.co/api/models?filter=stable-diffusion"),
        ("推理API状态", "https://huggingface.co/api/models/runwayml/stable-diffusion-v1-5"),
    ]
    
    for name, endpoint in api_endpoints:
        try:
            start_time = time.time()
            response = requests.get(endpoint, headers=headers, timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"✅ {name}API正常 - 响应时间: {response_time:.2f}s")
            else:
                print(f"⚠️  {name}API异常 - 状态码: {response.status_code}")
                if response.status_code == 401:
                    print("   可能原因: API密钥无效或过期")
                elif response.status_code == 403:
                    print("   可能原因: 权限不足")
                elif response.status_code == 404:
                    print("   可能原因: 模型不存在")
                    
        except requests.exceptions.Timeout:
            print(f"❌ {name}API超时")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ {name}连接错误: {e}")
        except Exception as e:
            print(f"❌ {name}其他错误: {e}")
    
    # 4. 测试推理API（模拟真实请求）
    print("\n🎨 测试图片生成API...")
    test_payload = {
        "inputs": "a cute cat",
        "options": {
            "wait_for_model": True,
            "use_cache": False
        }
    }
    
    models_to_test = [
        "runwayml/stable-diffusion-v1-5",
        "stabilityai/stable-diffusion-2-1",
    ]
    
    for model in models_to_test:
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        print(f"测试模型: {model}")
        
        try:
            start_time = time.time()
            response = requests.post(
                api_url,
                headers=headers,
                json=test_payload,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"  ✅ 生成成功 - 耗时: {response_time:.2f}s")
                # 检查返回内容
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    print(f"  ✅ 返回图片数据，大小: {len(response.content)} bytes")
                else:
                    print(f"  ⚠️  返回非图片数据: {content_type}")
                    
            elif response.status_code == 503:
                print(f"  ⚠️  模型加载中 - 状态码: 503")
                try:
                    error_info = response.json()
                    if "estimated_time" in error_info:
                        print(f"    预计等待时间: {error_info['estimated_time']:.1f}秒")
                except:
                    pass
                    
            else:
                print(f"  ❌ 请求失败 - 状态码: {response.status_code}")
                try:
                    error_info = response.json()
                    print(f"    错误信息: {error_info}")
                except:
                    print(f"    原始响应: {response.text[:200]}...")
                    
        except requests.exceptions.Timeout:
            print(f"  ❌ 请求超时 (30秒)")
        except requests.exceptions.ConnectionError as e:
            print(f"  ❌ 连接错误: {e}")
        except Exception as e:
            print(f"  ❌ 其他错误: {e}")
        
        print()  # 空行分隔

if __name__ == "__main__":
    detailed_diagnosis()