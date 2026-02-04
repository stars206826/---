#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试视频API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_video_api():
    """测试视频生成API"""
    print("=" * 60)
    print("🎬 测试视频生成API")
    print("=" * 60)
    
    test_cases = [
        {"text": "三星堆", "expected": "三星堆.mp4"},
        {"text": "青铜鼎", "expected": "2.mp4"},
        {"text": "文物", "expected": "video.mp4"},
        {"text": "2.mp4", "expected": "2.mp4"},  # 直接文件名
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test['text']}")
        print("-" * 60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/generate-video",
                json={"text": test['text']},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 状态: {response.status_code}")
                print(f"📦 返回: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get('success'):
                    video_url = result.get('video_url', '')
                    if test['expected'] in video_url:
                        print(f"✅ 映射正确: {video_url}")
                    else:
                        print(f"⚠️ 映射不符: 期望包含 {test['expected']}, 实际 {video_url}")
                else:
                    print(f"❌ 请求失败: {result.get('error', '未知错误')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"响应: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败: 服务器未启动")
            print("请先运行: python enhanced_backend_with_edge_tts.py")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_video_api()
