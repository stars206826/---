#!/usr/bin/env python3
"""
整合版后端服务器 - 旗舰演示版
功能 1：真·AI对话 (接入 SiliconFlow API，支持 DeepSeek/Qwen)
功能 2：定向视频演示 (中文输入 -> 映射数字文件名)
"""

import json
import logging
import sys
import os
import time
import random
import glob
from http.server import SimpleHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from urllib.parse import urlparse, unquote

# 依赖库检查
try:
    import requests
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# -----------------------------------------------------------------------------
# 配置与初始化
# -----------------------------------------------------------------------------
PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# 🔑 API 配置 (用于真·AI对话)
# ==========================================
# 您提供的 SiliconFlow Key
API_KEY = "sk-icmlygwecglrkvlnehccofuzdpqpksxhlmqsuzqqeteagsbn"

# ==========================================
# 🗺️ 视频映射表 (用于定向视频演示)
# ==========================================
VIDEO_MAP = {
    "大足石刻制造": "2.mp4",
    "石刻": "2.mp4",
    "青铜鼎": "1.mp4",
    "三星堆": "3.mp4"
}

# 静态知识库 (作为 Prompt 背景信息喂给 AI)
KNOWLEDGE_GRAPH = {
    "bronze_ding": {
        "id": "bronze_ding", "name": "巴渝青铜祭祀鼎", "era": "战国晚期",
        "summary": "典型的巴渝地区青铜礼器，用于重要祭祀场合，体现了巴人独特的审美与信仰。",
        "story": "我曾被埋藏在三峡的泥土之下两千年，见证了巴国的兴衰。",
        "craft": "采用复杂的范铸法制作，纹饰精美，代表了当时最高的冶金水平。"
    },
    "rock_carving": {
        "id": "rock_carving", "name": "大足石刻菩萨造像", "era": "南宋",
        "summary": "以精细入微的石刻工艺著称，体现了宋代石刻艺术与宗教思想的融合，是世界文化遗产。",
        "story": "匠人们悬在峭壁之上，一锤一凿刻出了我的面容，我是慈悲与智慧的化身。",
        "craft": "利用山势岩层，采用圆雕与高浮雕结合，色彩历经千年依然依稀可见。"
    },
    "boat_model": {
        "id": "boat_model", "name": "三峡古航运木船", "era": "明清时期",
        "summary": "再现古代三峡航运场景，是理解川江号子与水运历史的重要实物。",
        "story": "我承载着盐巴与茶叶，逆流而上，见证了纤夫们的汗水与号子声。",
        "craft": "采用柏木制作，榫卯结构，船底设计适应了三峡的险滩急流。"
    }
}

# -----------------------------------------------------------------------------
# 核心功能函数
# -----------------------------------------------------------------------------

def choose_action(question: str) -> str:
    # 简单的动作判断，也可以让 LLM 返回，这里保持简单
    q = (question or "").lower()
    if any(k in q for k in ["指", "哪", "看", "这里"]): return "point"
    if any(k in q for k in ["走", "离开", "去"]): return "walk"
    return "wave"

# 🔥【核心升级】真·LLM API 调用
# 🔥【核心升级】真·LLM API 调用 (修复乱码版)
def generate_llm_response(relic: dict, question: str, persona: str, style: str) -> str:
    """
    调用 SiliconFlow API 生成真实的角色扮演回复
    """
    logging.info(f"🤖 [AI对话] 收到提问: {question} (角色: {relic['name']})")

    # 1. 构建 Prompt (提示词)
    tone_instruction = ""
    if persona == "child":
        tone_instruction = "你的听众是小朋友，请用生动、简单、童话般的语言，像讲故事一样回答，多用语气词（如'哇'、'呀'）。"
    elif persona == "scholar":
        tone_instruction = "你的听众是专业学者，请用严谨、学术、历史感厚重的语言，引用历史背景。"
    else: # tourist
        tone_instruction = "你的听众是普通游客，请用热情、导游般通俗易懂的语言，多介绍有趣的点。"

    role_instruction = ""
    if style == "personified":
        role_instruction = f"请完全扮演'{relic['name']}'这个文物本身（第一人称'我'）。不要说'我是AI'。你有灵魂，有记忆。"
    else:
        role_instruction = f"请作为一名博物馆讲解员，客观介绍'{relic['name']}'。"

    system_prompt = (
        f"你现在是：{relic['name']}，处于{relic['era']}时代。\n"
        f"你的基本信息：{relic['summary']}\n"
        f"你的故事：{relic['story']}\n"
        f"你的工艺：{relic['craft']}\n\n"
        f"【指令】：\n"
        f"1. {role_instruction}\n"
        f"2. {tone_instruction}\n"
        f"3. 回答要控制在100字以内，不要输出乱码或无关信息。\n"
    )

    # 2. 调用 API
    try:
        url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            # 修改 1：换用更稳定的 Qwen 2.5 模型
            "model": "Qwen/Qwen2.5-72B-Instruct", 
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            # 修改 2：降低温度，减少胡言乱语
            "temperature": 0.3,
            "max_tokens": 200,
            "stream": False
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            result = resp.json()
            answer = result['choices'][0]['message']['content']
            # 简单的清洗，防止模型吐出多余的标签
            answer = answer.replace("<think>", "").replace("</think>", "").strip()
            logging.info(f"✅ [AI回复] {answer}")
            return answer
        else:
            logging.error(f"❌ API 错误: {resp.text}")
            return f"(AI 连接微弱) 我是{relic['name']}... 请稍后再试。"
            
    except Exception as e:
        logging.error(f"❌ 网络错误: {e}")
        return f"我是{relic['name']}。{relic['summary']} (离线模式)"    # 组合 System Prompt
    system_prompt = (
        f"你现在是：{relic['name']}，处于{relic['era']}时代。\n"
        f"你的基本信息：{relic['summary']}\n"
        f"你的故事：{relic['story']}\n"
        f"你的工艺：{relic['craft']}\n\n"
        f"【指令】：\n"
        f"1. {role_instruction}\n"
        f"2. {tone_instruction}\n"
        f"3. 回答要控制在100字以内，简练但精彩。\n"
    )

    # 2. 调用 API
    try:
        url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-ai/DeepSeek-V3", # 使用强大的 DeepSeek V3
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7,
            "max_tokens": 200,
            "stream": False
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            result = resp.json()
            answer = result['choices'][0]['message']['content']
            logging.info(f"✅ [AI回复] {answer}")
            return answer
        else:
            logging.error(f"❌ API 错误: {resp.text}")
            return f"(AI 连接微弱) 我是{relic['name']}... 请稍后再试。"
            
    except Exception as e:
        logging.error(f"❌ 网络错误: {e}")
        # 降级方案：如果断网，返回静态数据
        return f"我是{relic['name']}。{relic['summary']} (离线模式)"


def fetch_mapped_video(input_text: str) -> dict:
    """
    定向视频映射逻辑 (保持不变)
    """
    clean_text = input_text.strip()
    logging.info(f"🎬 [视频请求] 用户输入: '{clean_text}'")
    time.sleep(2.0) # 模拟加载感
    
    target_filename = VIDEO_MAP.get(clean_text)
    
    if not target_filename:
        if clean_text.endswith('.mp4'):
            target_filename = clean_text
        else:
            target_filename = f"{clean_text}.mp4"
    
    file_path = os.path.join(OUTPUT_DIR, target_filename)
    
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path) // 1024
        return {
            "success": True, 
            "video_url": f"/output/{target_filename}", 
            "fileSize": f"{file_size}KB", 
            "message": f"播放: {target_filename}"
        }
    else:
        # 找不到时的兜底：找第一个可用的mp4
        all_mp4 = glob.glob(os.path.join(OUTPUT_DIR, "*.mp4"))
        if all_mp4:
            fallback = os.path.basename(all_mp4[0])
            return {
                "success": True, 
                "video_url": f"/output/{fallback}", 
                "fileSize": "Cached", 
                "message": f"自动匹配: {fallback}"
            }
        else:
            return {"success": False, "error": "本地无视频"}

# -----------------------------------------------------------------------------
# HTTP服务器处理器
# -----------------------------------------------------------------------------

class IntegratedServerHandler(SimpleHTTPRequestHandler):
    
    def _send_json(self, payload, status_code: int = 200):
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        try:
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/api/relics":
            relics_list = [{"id": v["id"], "name": v["name"], "era": v["era"]} for k,v in KNOWLEDGE_GRAPH.items()]
            self._send_json(relics_list)
            
        elif parsed.path == "/api/team":
            # ==========================================
            # 👥 团队成员名单配置 (已同步 index.html 数据)
            # ==========================================
            self._send_json({
                # 1. 核心开发团队 (Core Developers)
                # 这里可以放技术骨干，如果没有具体区分，可以留空或把部分成员放这里
                "core_team": [
                    # 示例：把前两位作为核心开发展示，或者您可以留空 []
                    {"name": "周川力", "role": "核心成员", "avatar": "💻"},
                    {"name": "孟祥雨", "role": "核心成员", "avatar": "🧠"}
                ],
                
                # 2. 其他成员 (Special Operatives)
                "members": [
                    {"name": "李沁珊", "role": "团队成员", "avatar": "👾"},
                    {"name": "程小芸", "role": "团队成员", "avatar": "👾"},
                    {"name": "苏芯",   "role": "团队成员", "avatar": "👾"},
                    {"name": "刘海燕", "role": "团队成员", "avatar": "👾"},
                    {"name": "孙志一", "role": "团队成员", "avatar": "👾"},
                    {"name": "韦敦忆", "role": "团队成员", "avatar": "👾"},
                    {"name": "雷千",   "role": "团队成员", "avatar": "👾"},
                    {"name": "但宜珊", "role": "团队成员", "avatar": "👾"}
                ]
            })
        elif parsed.path.startswith("/output/") or parsed.path.startswith("/images/"):
            super().do_GET()
            
        elif parsed.path == "/" or parsed.path == "/index.html":
            try:
                with open("integrated_frontend.html", "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_error(404, "Frontend file not found")
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode('utf-8'))
        except:
            return

        if parsed.path == "/api/generate":
            # ==========================
            # 💬 对话接口 (真·AI)
            # ==========================
            rid = data.get("relic_id")
            relic = KNOWLEDGE_GRAPH.get(rid, {})
            # 调用真实 API
            ans = generate_llm_response(relic, data.get("question"), data.get("persona"), data.get("style"))
            self._send_json({"answer": ans, "action": choose_action(data.get("question"))})

        elif parsed.path == "/api/generate-video":
            # ==========================
            # 🎬 视频接口 (定向演示)
            # ==========================
            text = data.get("text", "")
            result = fetch_mapped_video(text)
            self._send_json(result)
        else:
            self.send_error(404)

def run_server():
    server_address = ('', PORT)
    httpd = ThreadingHTTPServer(server_address, IntegratedServerHandler)
    
    print("=" * 60)
    print(f"🚀 [旗舰演示版] 服务器已启动: http://localhost:{PORT}")
    print(f"💬 对话引擎: DeepSeek-V3 (Real API)")
    print(f"🎬 视频引擎: 定向映射模式 (输入'大足石刻' -> 播放 2.mp4)")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    run_server()