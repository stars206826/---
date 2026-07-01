#!/usr/bin/env python3
"""
增强版后端 - 集成Edge TTS自然语音
免费且效果优秀的语音合成解决方案
"""

import json
import logging
import sys
import os
import time
import random
import glob
import hashlib
import asyncio
from http.server import SimpleHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from urllib.parse import urlparse, unquote

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ 环境变量已加载")
except ImportError:
    print("⚠️ python-dotenv未安装，将使用系统环境变量")
    print("   提示: pip install python-dotenv")

# 导入原有的模块
try:
    import requests
except ImportError:
    print("请安装requests库: pip install requests")
    sys.exit(1)

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    print("警告: Neo4j驱动未安装，将使用静态知识库")
    NEO4J_AVAILABLE = False

# 尝试导入Edge TTS
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
    print("✅ Edge TTS语音服务可用")
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("⚠️ Edge TTS未安装，将使用浏览器语音合成")
    print("要启用自然语音，请运行: pip install edge-tts")

# 尝试导入 SeeDance 集成模块
try:
    from seedance_integration import (
        SeeDanceVideoGenerator,
        ConfigManager,
        ValidationError,
        APIError,
        TimeoutError as SeeDanceTimeoutError
    )
    SEEDANCE_MODULE_AVAILABLE = True
    print("✅ SeeDance 集成模块已加载")
except ImportError as e:
    SEEDANCE_MODULE_AVAILABLE = False
    print(f"⚠️ SeeDance 集成模块未找到: {e}")
    print("   SeeDance AI 视频生成功能将不可用")

# 豆包TTS已移除
DOUBAO_TTS_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# 配置
PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# API配置 - 从环境变量读取
API_KEY = os.getenv("SILICONFLOW_KEY", "sk-icmlygwecglrkvlnehccofuzdpqpksxhlmqsuzqqeteagsbn")

# Neo4j配置 - 从环境变量读取
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")

# 豆包语音服务配置（已禁用）
DOUBAO_CONFIG = {
    "enabled": False
}

# 视频映射表
VIDEO_MAP = {
    "大足石刻制造": "大足石刻制造.mp4",
    "大足石刻": "大足石刻制造.mp4",
    "石刻": "大足石刻制造.mp4",
    "青铜鼎制造": "青铜鼎制造.mp4",
    "青铜鼎": "青铜鼎制造.mp4",
    "青铜面具制造": "青铜面具制造.mp4",
    "青铜面具": "青铜面具制造.mp4",
    "三星堆": "青铜面具制造.mp4",
    "兵马俑出土": "兵马俑出土.mp4",
    "兵马俑": "兵马俑出土.mp4",
    "金缕玉衣": "金丝缕衣制造.mp4",
    "金丝缕衣": "金丝缕衣制造.mp4",
    "三峡古船": "三峡古航运木船制造.mp4",
    "古船": "三峡古航运木船制造.mp4"
}

# 静态知识库
STATIC_KNOWLEDGE_GRAPH = {
    "bronze_ding": {
        "id": "bronze_ding", "name": "巴渝青铜祭祀鼎", "era": "战国晚期",
        "summary": "典型的巴渝地区青铜礼器，用于重要祭祀场合，体现了巴人独特的审美与信仰。",
        "story": "我曾被埋藏在三峡的泥土之下两千年，见证了巴国的兴衰。",
        "craft": "采用复杂的范铸法制作，纹饰精美，代表了当时最高的冶金水平。",
        "relations": ["与巴国文化相关", "属于青铜器类别", "用于祭祀仪式"]
    },
    "rock_carving": {
        "id": "rock_carving", "name": "大足石刻菩萨造像", "era": "南宋",
        "summary": "以精细入微的石刻工艺著称，体现了宋代石刻艺术与宗教思想的融合，是世界文化遗产。",
        "story": "匠人们悬在峭壁之上，一锤一凿刻出了我的面容，我是慈悲与智慧的化身。",
        "craft": "利用山势岩层，采用圆雕与高浮雕结合，色彩历经千年依然依稀可见。",
        "relations": ["属于佛教艺术", "世界文化遗产", "宋代石刻代表"]
    },
    "boat_model": {
        "id": "boat_model", "name": "三峡古航运木船", "era": "明清时期",
        "summary": "再现古代三峡航运场景，是理解川江号子与水运历史的重要实物。",
        "story": "我承载着盐巴与茶叶，逆流而上，见证了纤夫们的汗水与号子声。",
        "craft": "采用柏木制作，榫卯结构，船底设计适应了三峡的险滩急流。",
        "relations": ["三峡文化载体", "古代交通工具", "川江号子相关"]
    },
    "sanxingdui_bronze_mask": {
        "id": "sanxingdui_bronze_mask", "name": "三星堆青铜面具", "era": "商代晚期",
        "summary": "三星堆遗址出土的神秘青铜面具，具有突出的眼球和夸张的造型，体现了古蜀文明独特的艺术风格。",
        "story": "我是来自古蜀王国的神秘面具，在地下沉睡了三千多年。我的眼睛如此突出，是为了更好地观察天地万物。我见证了古蜀文明的辉煌，那时的工匠们用最精湛的技艺塑造了我，让我成为沟通神灵与人间的桥梁。",
        "craft": "失蜡法铸造工艺：首先用蜂蜡制作面具模型，然后用细泥包裹蜡模形成外范，加热使蜡液流出形成空腔，再将熔化的青铜液倒入空腔中。冷却后打破泥范，就得到了青铜面具。表面采用鎏金工艺，将金汞合金涂在青铜表面，加热使汞蒸发，金就牢固地附着在青铜上，呈现出金光闪闪的效果。",
        "relations": ["古蜀文明代表", "青铜器类别", "宗教祭祀用品", "考古重大发现"]
    },
    "terracotta_warrior": {
        "id": "terracotta_warrior", "name": "兵马俑武士俑", "era": "秦代",
        "summary": "秦始皇陵兵马俑坑出土的武士俑，身高约1.8米，神态威严，是秦代军事文化的杰出代表。",
        "story": "我是秦始皇的地下军团中的一员，两千多年来一直守护着皇陵。每一个兄弟都有着不同的面容，我们代表着大秦帝国的威武之师。虽然是陶土制成，但我们的心中依然燃烧着保卫帝国的忠诚之火。",
        "craft": "兵马俑采用分段制作工艺：先用陶轮制作身体各部分，头部、躯干、四肢分别制作。头部用模具压制基本形状，再手工雕刻面部细节，每个俑的表情都不相同。身体部分采用泥条盘筑法，一层层堆砌成型。各部分制作完成后进行组装，接缝处用泥浆粘合。整体成型后在表面涂抹细泥，精修细节。最后入窑烧制，温度控制在950-1000度，烧制时间约15-20天。",
        "relations": ["秦代文化", "陶俑类别", "军事文化", "世界文化遗产"]
    },
    "jade_burial_suit": {
        "id": "jade_burial_suit", "name": "金缕玉衣", "era": "西汉",
        "summary": "西汉中山靖王刘胜的金缕玉衣，由2498片玉片用金丝连缀而成，是汉代丧葬文化的珍贵实物。",
        "story": "我是为中山靖王刘胜量身定制的永恒之衣。每一片玉都经过精心挑选，每一根金丝都承载着对永生的渴望。古人相信玉能保持尸身不腐，而我就是这种信念的完美体现。穿上我，就能在另一个世界继续享受荣华富贵。",
        "craft": "金缕玉衣制作工艺极其复杂：首先要选择优质的和田玉，按照人体各部位的形状切割成2498片大小不等的玉片。每片玉片都要经过切割、打磨、钻孔三道工序。切割使用铜质线锯配合解玉砂，打磨用细砂石反复研磨至光滑，然后在四角钻出细孔。金丝制作需要将黄金拉成细丝，直径仅0.1毫米。最后按照人体结构，用金丝将玉片逐一串联编织，形成完整的玉衣。",
        "relations": ["汉代文化", "玉器类别", "丧葬文化", "皇室文物"]
    }
}

class EdgeTTSService:
    """Edge TTS语音服务类"""
    
    def __init__(self):
        self.available = EDGE_TTS_AVAILABLE
        if self.available:
            logging.info("✅ Edge TTS语音服务已初始化")
        else:
            logging.info("⚠️ Edge TTS语音服务不可用，将使用浏览器语音合成")
    
    def get_voice_config(self, persona: str, style: str):
        """获取语音配置"""
        voice_configs = {
            'child': {
                'voice': 'zh-CN-XiaoxiaoNeural',
                'rate': '-20%',
                'pitch': '+10Hz',
                'volume': '+0%'
            },
            'scholar': {
                'voice': 'zh-CN-YunxiNeural',
                'rate': '-30%',
                'pitch': '-10Hz',
                'volume': '-10%'
            },
            'tourist': {
                'voice': 'zh-CN-XiaoyiNeural',
                'rate': '-10%',
                'pitch': '+5Hz',
                'volume': '+5%'
            }
        }
        
        config = voice_configs.get(persona, voice_configs['tourist'])
        
        if style == 'personified':
            # 调整音调（增加5Hz）
            current_pitch = int(config['pitch'].replace('Hz', '').replace('+', '').replace('-', ''))
            new_pitch = current_pitch + 5
            config['pitch'] = f"+{new_pitch}Hz" if new_pitch >= 0 else f"{new_pitch}Hz"
            
            # 调整语速（增加5%）
            current_rate = int(config['rate'].replace('%', '').replace('+', '').replace('-', ''))
            new_rate = current_rate + 5
            config['rate'] = f"+{new_rate}%" if new_rate > 0 else f"{new_rate}%"
        
        return config
    
    def create_ssml(self, text: str, persona: str, style: str):
        """创建SSML"""
        config = self.get_voice_config(persona, style)
        
        # 处理情感标记
        processed_text = text
        processed_text = processed_text.replace('！', '<emphasis level="strong">！</emphasis>')
        processed_text = processed_text.replace('!', '<emphasis level="strong">!</emphasis>')
        processed_text = processed_text.replace('...', '<break time="800ms"/>')
        processed_text = processed_text.replace('？', '<prosody pitch="+15%">？</prosody>')
        processed_text = processed_text.replace('?', '<prosody pitch="+15%">?</prosody>')
        
        # 情感词汇处理
        emotional_words = {
            '哇': '<emphasis level="strong"><prosody pitch="+20%">哇</prosody></emphasis>',
            '哎呀': '<emphasis level="moderate">哎呀</emphasis>',
            '嘿嘿': '<prosody rate="-20%">嘿嘿</prosody>',
            '哼': '<emphasis level="strong">哼</emphasis>',
            '唉': '<prosody pitch="-20%" rate="-30%">唉</prosody>',
            '你知道吗': '<prosody pitch="+10%">你知道吗</prosody>',
            '猜猜看': '<prosody pitch="+15%">猜猜看</prosody>',
            '想当年': '<prosody rate="-20%">想当年</prosody>',
            '那时候': '<prosody rate="-15%">那时候</prosody>'
        }
        
        for word, replacement in emotional_words.items():
            processed_text = processed_text.replace(word, replacement)
        
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
               xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
            <voice name="{config['voice']}">
                <prosody rate="{config['rate']}" pitch="{config['pitch']}" volume="{config['volume']}">
                    {processed_text}
                </prosody>
            </voice>
        </speak>
        """
        
        return ssml
    
    async def synthesize_speech_async(self, text: str, persona: str, style: str):
        """异步合成语音"""
        if not self.available:
            return None
        
        try:
            config = self.get_voice_config(persona, style)
            
            # Edge TTS不需要SSML，直接传入纯文本和语音参数
            # 使用Communicate的rate, pitch, volume参数
            communicate = edge_tts.Communicate(
                text=text,
                voice=config['voice'],
                rate=config['rate'],
                pitch=config['pitch'],
                volume=config['volume']
            )
            
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            return audio_data
            
        except Exception as e:
            logging.error(f"Edge TTS语音合成异常: {e}")
            return None
    
    def synthesize_speech(self, text: str, persona: str, style: str):
        """同步合成语音"""
        if not self.available:
            return None
        
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                return loop.run_until_complete(
                    self.synthesize_speech_async(text, persona, style)
                )
            finally:
                loop.close()
                
        except Exception as e:
            logging.error(f"语音合成失败: {e}")
            return None

# 初始化Edge TTS服务
edge_tts_service = EdgeTTSService()

# 豆包TTS服务已移除
doubao_tts_service = None
logging.info("📦 豆包TTS功能已禁用")

# 初始化 SeeDance 视频生成器
seedance_generator = None
SEEDANCE_AVAILABLE = False

if SEEDANCE_MODULE_AVAILABLE:
    try:
        # 创建配置管理器
        seedance_config = ConfigManager()
        
        # 检查 API 密钥是否配置
        api_key = seedance_config.get("api.key")
        if api_key:
            # 创建视频生成器，传入降级函数
            seedance_generator = SeeDanceVideoGenerator(
                config=seedance_config,
                fallback_func=fetch_mapped_video  # 将在后面定义
            )
            SEEDANCE_AVAILABLE = True
            logging.info("✅ SeeDance 2.0 AI视频生成可用")
        else:
            logging.warning("⚠️ SeeDance API 密钥未配置")
            logging.info("   请设置 SEEDANCE_API_KEY 环境变量或在 seedance_config.json 中配置")
    except Exception as e:
        logging.error(f"❌ SeeDance 初始化失败: {e}")
        logging.info("   SeeDance AI 视频生成功能将不可用")
else:
    logging.info("📹 SeeDance 模块未加载，仅使用本地视频功能")

# Neo4j知识图谱类（简化版，复用原有代码）
class Neo4jKnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = None
        self.connected = False
        
        if NEO4J_AVAILABLE:
            try:
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
                with self.driver.session() as session:
                    session.run("RETURN 1")
                self.connected = True
                logging.info("✅ Neo4j数据库连接成功")
            except Exception as e:
                logging.warning(f"⚠️ Neo4j连接失败: {e}")
                logging.info("🔄 将使用静态知识库作为降级方案")
        else:
            logging.info("📚 使用静态知识库模式")
    
    def get_artifact_info(self, artifact_id):
        """获取文物基本信息"""
        if not self.connected:
            return STATIC_KNOWLEDGE_GRAPH.get(artifact_id, {})
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a:Artifact {id: $artifact_id})
                    RETURN a
                """, artifact_id=artifact_id)
                
                record = result.single()
                if record:
                    return dict(record["a"])
                else:
                    return STATIC_KNOWLEDGE_GRAPH.get(artifact_id, {})
        except Exception as e:
            logging.error(f"❌ Neo4j查询失败: {e}")
            return STATIC_KNOWLEDGE_GRAPH.get(artifact_id, {})
    
    def get_related_artifacts(self, artifact_id):
        """获取相关文物"""
        if not self.connected:
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a1:Artifact {id: $artifact_id})-[:BELONGS_TO_ERA|LOCATED_IN|BELONGS_TO_CATEGORY]-(common)-[:BELONGS_TO_ERA|LOCATED_IN|BELONGS_TO_CATEGORY]-(a2:Artifact)
                    WHERE a1 <> a2
                    RETURN DISTINCT a2.name as name, a2.id as id, a2.era as era
                    LIMIT 5
                """, artifact_id=artifact_id)
                
                return [dict(record) for record in result]
        except Exception as e:
            logging.error(f"❌ Neo4j关系查询失败: {e}")
            return []
    
    def get_knowledge_context_with_source(self, artifact_id, question):
        """根据问题获取相关知识上下文，并返回数据源信息"""
        artifact_info = self.get_artifact_info(artifact_id)
        related_artifacts = self.get_related_artifacts(artifact_id)
        
        # 确定数据源
        if self.connected:
            data_source = {
                "type": "neo4j",
                "status": "connected",
                "description": "Neo4j知识图谱",
                "features": ["关联查询", "语义推理", "动态关系"]
            }
        else:
            data_source = {
                "type": "static",
                "status": "fallback",
                "description": "静态知识库",
                "features": ["基础信息", "预设内容"]
            }
        
        context = f"文物信息: {artifact_info}\n"
        
        if related_artifacts and self.connected:
            context += f"相关文物: {related_artifacts}\n"
            context += f"[数据来源: Neo4j图数据库关联查询]\n"
        elif not self.connected:
            context += f"[数据来源: 静态知识库]\n"
        
        # 根据问题关键词添加特定上下文
        question_lower = question.lower()
        if any(keyword in question_lower for keyword in ["历史", "时代", "年代"]):
            context += f"历史背景: 该文物属于{artifact_info.get('era', '未知')}时期\n"
        
        if any(keyword in question_lower for keyword in ["工艺", "制作", "技术"]):
            context += f"制作工艺: {artifact_info.get('craft', '传统工艺')}\n"
        
        if any(keyword in question_lower for keyword in ["地点", "位置", "哪里"]):
            context += f"地理位置: {artifact_info.get('location', '未知地区')}\n"
        
        return context, data_source
    
    def get_data_source_info(self):
        if self.connected:
            return {
                "type": "neo4j",
                "status": "connected", 
                "name": "Neo4j知识图谱",
                "icon": "🗄️"
            }
        else:
            return {
                "type": "static",
                "status": "fallback",
                "name": "静态知识库", 
                "icon": "📚"
            }
    
    def get_graph_data(self):
        """获取知识图谱数据用于可视化"""
        if not self.connected:
            # 返回静态数据
            nodes = [
                {"id": k, "name": v["name"], "type": "文物"} 
                for k, v in STATIC_KNOWLEDGE_GRAPH.items()
            ]
            return {
                "status": "static",
                "nodes": nodes,
                "edges": []
            }
        
        try:
            with self.driver.session() as session:
                # 获取所有节点，确保每个节点都有ID
                nodes_result = session.run("""
                    MATCH (n)
                    RETURN 
                        COALESCE(n.id, n.name, toString(id(n))) as id, 
                        n.name as name, 
                        labels(n)[0] as type
                    LIMIT 50
                """)
                nodes = [dict(record) for record in nodes_result]
                
                # 获取所有关系，确保source和target都有有效ID
                edges_result = session.run("""
                    MATCH (a)-[r]->(b)
                    RETURN 
                        COALESCE(a.id, a.name, toString(id(a))) as source, 
                        COALESCE(b.id, b.name, toString(id(b))) as target, 
                        type(r) as relationship
                    LIMIT 100
                """)
                edges = [dict(record) for record in edges_result]
                
                return {
                    "status": "neo4j_connected",
                    "nodes": nodes,
                    "edges": edges
                }
        except Exception as e:
            logging.error(f"❌ 获取图谱数据失败: {e}")
            # 降级到静态数据
            nodes = [
                {"id": k, "name": v["name"], "type": "文物"} 
                for k, v in STATIC_KNOWLEDGE_GRAPH.items()
            ]
            return {
                "status": "static",
                "nodes": nodes,
                "edges": []
            }
    
    def compare_relics(self, relic_a_id: str, relic_b_id: str):
        """对比两个文物"""
        relic_a = self.get_artifact_info(relic_a_id)
        relic_b = self.get_artifact_info(relic_b_id)
        
        if not relic_a or not relic_b:
            return {
                "error": "文物信息不存在"
            }
        
        # 分析共同点
        commonalities = []
        
        # 时代对比
        if relic_a.get('era') == relic_b.get('era'):
            commonalities.append(f"都属于{relic_a.get('era')}时期")
        
        # 地区对比
        if relic_a.get('location') and relic_b.get('location'):
            if relic_a.get('location') == relic_b.get('location'):
                commonalities.append(f"都来自{relic_a.get('location')}地区")
        
        # 类别对比
        if relic_a.get('category') and relic_b.get('category'):
            if relic_a.get('category') == relic_b.get('category'):
                commonalities.append(f"都属于{relic_a.get('category')}类别")
        
        # 用途对比
        if 'relations' in relic_a and 'relations' in relic_b:
            common_relations = set(relic_a['relations']) & set(relic_b['relations'])
            if common_relations:
                for rel in common_relations:
                    commonalities.append(rel)
        
        # 分析差异点
        differences = []
        
        # 时代差异
        if relic_a.get('era') != relic_b.get('era'):
            differences.append(f"时代不同：{relic_a.get('name')}属于{relic_a.get('era')}，{relic_b.get('name')}属于{relic_b.get('era')}")
        
        # 工艺差异
        if relic_a.get('craft') and relic_b.get('craft'):
            if relic_a.get('craft') != relic_b.get('craft'):
                differences.append(f"工艺不同：{relic_a.get('name')}采用{relic_a.get('craft')[:20]}...，{relic_b.get('name')}采用{relic_b.get('craft')[:20]}...")
        
        # 材质差异（从名称推断）
        materials_a = []
        materials_b = []
        if '青铜' in relic_a.get('name', ''):
            materials_a.append('青铜')
        if '石' in relic_a.get('name', ''):
            materials_a.append('石材')
        if '木' in relic_a.get('name', ''):
            materials_a.append('木材')
        
        if '青铜' in relic_b.get('name', ''):
            materials_b.append('青铜')
        if '石' in relic_b.get('name', ''):
            materials_b.append('石材')
        if '木' in relic_b.get('name', ''):
            materials_b.append('木材')
        
        if materials_a and materials_b and materials_a != materials_b:
            differences.append(f"材质不同：{relic_a.get('name')}为{'、'.join(materials_a)}制品，{relic_b.get('name')}为{'、'.join(materials_b)}制品")
        
        # 如果没有找到明显差异，添加通用描述
        if not differences:
            differences.append(f"{relic_a.get('name')}和{relic_b.get('name')}各具特色，体现了不同的文化内涵")
        
        return {
            "relic_a": relic_a,
            "relic_b": relic_b,
            "commonalities": commonalities,
            "differences": differences
        }

# 初始化知识图谱
kg = Neo4jKnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

def clean_text_for_speech(text: str) -> str:
    """
    清理文本，使其更适合语音播放
    移除所有可能导致语音合成读出英文或数字的字符
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的纯中文文本
    """
    import re
    
    # 1. 移除markdown格式标记
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # 粗体 **text**
    text = re.sub(r'\*(.+?)\*', r'\1', text)      # 斜体 *text*
    text = re.sub(r'__(.+?)__', r'\1', text)      # 下划线 __text__
    text = re.sub(r'`(.+?)`', r'\1', text)        # 代码 `text`
    text = re.sub(r'~~(.+?)~~', r'\1', text)      # 删除线 ~~text~~
    
    # 2. 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 3. 将英文省略号替换为中文省略号
    text = text.replace('...', '…')
    text = text.replace('..', '…')
    
    # 4. 将英文标点替换为中文标点
    punctuation_map = {
        ',': '，',
        '.': '。',
        '!': '！',
        '?': '？',
        ';': '；',
        ':': '：',
        '(': '（',
        ')': '）',
        '[': '【',
        ']': '】',
        '"': '"',
        '<': '《',
        '>': '》',
    }
    for eng, chn in punctuation_map.items():
        text = text.replace(eng, chn)
    
    # 替换单引号（使用chr避免语法错误）
    text = text.replace(chr(39), chr(8217))  # ' -> '
    
    # 5. 移除所有英文字母（如果有的话）
    text = re.sub(r'[a-zA-Z]+', '', text)
    
    # 6. 移除所有阿拉伯数字（如果有的话）
    # 注意：如果需要保留数字并转换为中文，可以使用number_to_chinese函数
    text = re.sub(r'\d+', '', text)
    
    # 7. 移除emoji和其他特殊符号
    # 只保留：中文字符、中文标点、空格、换行
    text = re.sub(r'[^\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef，。！？、；：""''（）《》【】…—\s]', '', text)
    
    # 8. 清理多余的空格和换行
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # 9. 清理连续的标点符号
    text = re.sub(r'([，。！？、；：…])\1+', r'\1', text)
    
    # 10. 移除可能的特殊空格字符
    text = text.replace('\u200b', '')  # 零宽空格
    text = text.replace('\xa0', ' ')   # 不间断空格
    
    return text

def generate_llm_response(relic: dict, question: str, persona: str, style: str) -> str:
    """
    调用 SiliconFlow API 生成基于Neo4j知识图谱的AI回复
    """
    logging.info(f"🤖 [AI对话] 收到提问: {question} (角色: {relic.get('name', '未知文物')})")

    # 获取知识图谱上下文和数据源信息
    knowledge_context, data_source = kg.get_knowledge_context_with_source(relic.get('id', ''), question)
    
    # 构建更生动的语调指令 - 增强版
    tone_instruction = ""
    if persona == "child":
        tone_instruction = """你的听众是小朋友，请用：
        - 生动活泼的语言，像最会讲故事的奶奶一样温暖
        - 丰富的语气词：'哇塞！'、'哎呀！'、'咦？'、'嘿嘿'、'哦～'
        - 拟声词让故事活起来：'叮叮当当'、'咚咚咚'、'嗖嗖嗖'、'哗啦啦'
        - 语调要有戏剧性起伏，像在表演一样
        - 多用疑问句互动：'你猜猜看？'、'知道为什么吗？'
        - 用比喻让复杂的事情变简单：'就像...'、'好比...'"""
    elif persona == "scholar":
        tone_instruction = """你的听众是专业学者，请用：
        - 深沉而富有学者气质的语调，带着历史的厚重感
        - 思辨性的停顿：'嗯...让我想想'、'你看啊...'、'实际上呢...'
        - 引用具体的历史细节，展现博学
        - 语调要庄重但充满感情，偶尔流露出对历史的感慨
        - 用学术性的表达：'从历史角度来看...'、'根据考古发现...'
        - 适当的哲思：'这让我想到...'、'历史总是...'"""
    else: # tourist
        tone_instruction = """你的听众是普通游客，请用：
        - 热情洋溢的导游语调，充满感染力
        - 亲切的开场：'朋友们！'、'您知道吗？'、'来来来，听我说'
        - 制造悬念和惊喜：'猜猜看...'、'更神奇的是...'、'你绝对想不到...'
        - 通俗易懂但不失趣味：'说白了就是...'、'简单来说...'
        - 互动性强：'是不是很有趣？'、'您觉得呢？'
        - 热情的结尾：'怎么样，厉害吧！'、'是不是很神奇？'"""

    # 增强角色扮演指令 - 让文物真正"活"起来
    role_instruction = ""
    if style == "personified":
        role_instruction = f"""请完全扮演'{relic.get('name', '文物')}'这个文物本身：
        - 用第一人称'我'，你就是这个文物，有血有肉有灵魂
        - 展现丰富的情感层次：
          * 骄傲时：'哼，我可是...'、'当年我...'
          * 怀念时：'那时候啊...'、'想当初...'
          * 调皮时：'嘿嘿，告诉你个秘密...'
          * 感慨时：'唉，岁月如流...'
        - 用你独特的视角看世界：'你们现代人啊...'、'我见过的人多了去了...'
        - 展现文物的智慧和阅历：'经历了这么多，我明白了...'
        - 偶尔"卖个关子"：'这个嘛...让我想想要不要告诉你'
        - 语言要有生命力，让人感受到你真的在呼吸、在思考"""
    else:
        role_instruction = f"""请作为一名充满激情的博物馆讲解员：
        - 对'{relic.get('name', '文物')}'充满深深的热爱和敬意
        - 语调要有强烈的感染力，能点燃听众的兴趣
        - 适当表达你的赞叹：'真是太精美了！'、'简直不敢相信！'
        - 像一个博学而亲切的朋友在分享珍贵的故事
        - 偶尔流露出专业的骄傲：'这可是我们的镇馆之宝！'
        - 用生动的描述让文物在听众心中"复活"：'仿佛能听到...'、'好像看到了...'"""

    # 语音优化指令 - 情感表达增强版
    voice_optimization = """
    【语音播放优化 - 让声音充满感情】：
    
    🎭 情感表达技巧：
    - 兴奋激动：多用"哇！"、"太棒了！"、"真的吗？！"
    - 神秘悬疑：用"你知道吗..."、"有个秘密..."、"猜猜看..."
    - 温柔回忆：用"那时候啊..."、"想当年..."、"记得..."
    - 骄傲自豪：用"哼！"、"当然啦！"、"我可是..."
    - 感慨沧桑：用"唉..."、"岁月如流..."、"经历了这么多..."
    
    🎵 语调节奏控制：
    - 重要信息前的停顿：'听着...这很重要'
    - 制造悬念：'你绝对想不到...竟然是...'
    - 情感递进：'不仅如此，更神奇的是...'
    - 互动提问：'你觉得呢？'、'是不是很有趣？'
    
    🎪 语气词的艺术运用：
    - 开场吸引：'哎呀！'、'哇塞！'、'天哪！'
    - 过渡连接：'不过呢'、'说起来'、'对了'、'还有啊'
    - 强调重点：'要知道'、'听好了'、'特别是'、'关键是'
    - 亲切结尾：'怎么样？'、'明白了吗？'、'有趣吧？'
    
    🎨 个性化表达：
    - 根据文物性格调整语调：古朴的用深沉语调，精美的用优雅语调
    - 展现"小脾气"：'哼，你们现代人啊...'、'我才不告诉你呢...'
    - 卖萌撒娇：'人家已经很努力了嘛...'、'不要嫌弃我老啦...'
    - 智慧感悟：'活了这么久，我明白了...'、'时间教会了我...'
    
    🎯 语音播放专用格式：
    - 多用短句，避免超长句子
    - 关键词重复：'很重要，真的很重要'
    - 数字用中文：'两千年' 而不是 '2000年'
    - 适当的拟声词：'叮叮当当'、'哗啦啦'、'咚咚咚'
    """

    system_prompt = (
        f"你现在是：{relic.get('name', '文物')}，处于{relic.get('era', '古代')}时代。\n"
        f"基于以下知识图谱信息回答问题：\n{knowledge_context}\n\n"
        f"【核心指令】：\n"
        f"1. {role_instruction}\n\n"
        f"2. {tone_instruction}\n\n"
        f"3. {voice_optimization}\n\n"
        f"4. 回答控制在120-180字，充分利用知识图谱中的关联信息。\n"
        f"5. 如果问题涉及相关文物，可以适当提及它们的关系。\n"
        f"6. 数据来源：{data_source['description']}，具备{', '.join(data_source['features'])}功能。\n\n"
        f"【重要】：你的回答将通过语音合成播放，请让每一句话都充满生命力和感情色彩！"
    )

    # 调用 API
    try:
        url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "Qwen/Qwen2.5-72B-Instruct", 
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7,  # 提高创造性，让回答更灵动
            "max_tokens": 150,   # 减少回答长度，适合语音播放
            "stream": False
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            result = resp.json()
            answer = result['choices'][0]['message']['content']
            answer = answer.replace("<think>", "").replace("</think>", "").strip()
            
            # 清理文本，使其更适合语音播放
            answer = clean_text_for_speech(answer)
            
            logging.info(f"✅ [AI回复] {answer}")
            return answer
        else:
            logging.error(f"❌ API 错误: {resp.text}")
            return f"(AI 连接微弱) 我是{relic.get('name', '文物')}... 请稍后再试。"
            
    except Exception as e:
        logging.error(f"❌ 网络错误: {e}")
        return f"我是{relic.get('name', '文物')}。{relic.get('summary', '一件珍贵的文物')} (离线模式)"

def fetch_mapped_video(input_text: str) -> dict:
    """
    定向视频映射逻辑
    根据用户输入的关键词，映射到对应的视频文件
    """
    clean_text = input_text.strip()
    logging.info(f"🎬 [视频请求] 用户输入: '{clean_text}'")
    time.sleep(0.5)  # 短暂延迟，模拟处理
    
    # 首先尝试从VIDEO_MAP中查找
    target_filename = VIDEO_MAP.get(clean_text)
    
    # 如果没找到，尝试直接使用输入作为文件名
    if not target_filename:
        if clean_text.endswith('.mp4'):
            target_filename = clean_text
        else:
            target_filename = f"{clean_text}.mp4"
    
    # 检查文件是否存在
    file_path = os.path.join(OUTPUT_DIR, target_filename)
    
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path) // 1024
        logging.info(f"✅ [视频] 找到文件: {target_filename} ({file_size}KB)")
        return {
            "success": True, 
            "video_url": f"/output/{target_filename}", 
            "fileSize": f"{file_size}KB", 
            "message": f"播放: {target_filename}"
        }
    else:
        # 如果指定文件不存在，尝试查找output目录下的任何mp4文件作为降级
        all_mp4 = glob.glob(os.path.join(OUTPUT_DIR, "*.mp4"))
        if all_mp4:
            fallback = os.path.basename(all_mp4[0])
            logging.warning(f"⚠️ [视频] 未找到 {target_filename}，使用降级: {fallback}")
            return {
                "success": True, 
                "video_url": f"/output/{fallback}", 
                "fileSize": "Cached", 
                "message": f"自动匹配: {fallback}"
            }
        else:
            logging.error(f"❌ [视频] 未找到任何视频文件")
            return {
                "success": False, 
                "error": "本地无视频文件",
                "message": "请确保output目录中有视频文件"
            }

class EnhancedServerHandler(SimpleHTTPRequestHandler):
    
    def _send_json(self, payload, status_code: int = 200):
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        try:
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass
    
    def _send_audio(self, audio_data, filename):
        """发送音频数据"""
        try:
            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(audio_data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(audio_data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        logging.info(f"GET请求路径: {parsed.path}")
        
        if parsed.path == "/api/speech-status":
            logging.info("处理语音状态API请求")
            # 返回语音服务状态（豆包已移除）
            edge_available = edge_tts_service.available
            
            # 构建可用服务列表
            available_services = []
            if edge_available:
                available_services.append("edge_tts")
            available_services.append("browser")  # 浏览器语音始终可用
            
            # 确定当前服务
            if edge_available:
                current_service = "edge_tts"
            else:
                current_service = "browser"
            
            # 构建状态消息
            if edge_available:
                message = "Edge TTS自然语音可用"
            else:
                message = "使用浏览器语音合成"
            
            self._send_json({
                "edge_tts_available": edge_available,
                "doubao_available": False,
                "current_service": current_service,
                "available_services": available_services,
                "fallback_to_browser": not edge_available,
                "message": message,
                "service_type": current_service
            })
            return
            
        elif parsed.path == "/api/relics":
            # 返回文物列表
            relics_list = [{"id": k, "name": v["name"], "era": v["era"]} for k, v in STATIC_KNOWLEDGE_GRAPH.items()]
            self._send_json(relics_list)
            return
        
        elif parsed.path == "/api/knowledge-graph":
            logging.info("📊 处理知识图谱请求")
            # 返回知识图谱数据
            graph_data = kg.get_graph_data()
            self._send_json(graph_data)
            return
        
        elif parsed.path == "/api/seedance-status":
            logging.info("📊 处理 SeeDance 状态查询")
            # 返回 SeeDance 状态信息
            status_info = {
                "available": SEEDANCE_AVAILABLE,
                "api_configured": False,
                "cache_enabled": False,
                "fallback_enabled": True
            }
            
            if SEEDANCE_AVAILABLE and seedance_generator:
                try:
                    status_info["api_configured"] = bool(seedance_generator.config.get("api.key"))
                    status_info["cache_enabled"] = seedance_generator.config.get("cache.enabled", True)
                    status_info["fallback_enabled"] = seedance_generator.config.get("fallback.enabled", True)
                except Exception as e:
                    logging.error(f"❌ 获取 SeeDance 状态失败: {e}")
            
            self._send_json(status_info)
            return
            
        elif parsed.path.startswith("/audio/"):
            # 提供音频文件服务
            audio_file = parsed.path[7:]
            file_path = os.path.join(AUDIO_DIR, audio_file)
            
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    audio_data = f.read()
                self._send_audio(audio_data, audio_file)
            else:
                self.send_error(404, "Audio file not found")
        
        elif parsed.path.startswith("/output/"):
            # 提供视频文件服务
            video_file = parsed.path[8:]
            file_path = os.path.join(OUTPUT_DIR, video_file)
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        video_data = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "video/mp4")
                    self.send_header("Content-Length", str(len(video_data)))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(video_data)
                    logging.info(f"✅ [视频] 已发送: {video_file}")
                except (BrokenPipeError, ConnectionResetError):
                    logging.warning(f"⚠️ [视频] 客户端连接中断: {video_file}")
                    pass
            else:
                logging.error(f"❌ [视频] 文件不存在: {file_path}")
                self.send_error(404, "Video file not found")
                
        elif parsed.path == "/" or parsed.path == "/index.html":
            # 提供主页面
            try:
                with open("enhanced_frontend.html", "rb") as f:
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
        logging.info(f"📥 POST请求: {parsed.path}")
        
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode('utf-8'))
            logging.info(f"✅ 请求数据解析成功")
        except Exception as e:
            logging.error(f"❌ JSON解析失败: {e}")
            self.send_error(400, "Invalid JSON")
            return

        if parsed.path == "/api/synthesize-speech":
            logging.info("🎤 处理Edge TTS请求")
            # Edge TTS语音合成接口 - 直接返回音频流
            text = data.get("text", "")
            persona = data.get("persona", "tourist")
            style = data.get("style", "guide")
            
            if not text:
                self._send_json({"error": "缺少文本内容"}, 400)
                return
            
            if edge_tts_service.available:
                # 使用Edge TTS合成
                audio_data = edge_tts_service.synthesize_speech(text, persona, style)
                
                if audio_data:
                    # 直接返回音频数据流，不保存文件
                    try:
                        self.send_response(200)
                        self.send_header("Content-Type", "audio/mpeg")
                        self.send_header("Content-Length", str(len(audio_data)))
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.send_header("Cache-Control", "public, max-age=3600")
                        self.end_headers()
                        self.wfile.write(audio_data)
                        logging.info(f"✅ [Edge TTS] 音频流已发送，大小: {len(audio_data)} bytes")
                    except (BrokenPipeError, ConnectionResetError):
                        logging.warning("⚠️ [Edge TTS] 客户端连接中断")
                        pass
                else:
                    self._send_json({
                        "success": False,
                        "error": "Edge TTS语音合成失败",
                        "fallback": True
                    })
            else:
                self._send_json({
                    "success": False,
                    "fallback": True,
                    "message": "Edge TTS服务不可用，请使用浏览器语音合成"
                })
        
        
        elif parsed.path == "/api/generate":
            logging.info("💬 处理AI对话请求")
            # AI对话接口
            rid = data.get("relic_id")
            relic = kg.get_artifact_info(rid)
            
            if not relic:
                relic = STATIC_KNOWLEDGE_GRAPH.get(rid, {})
            
            answer = generate_llm_response(relic, data.get("question"), data.get("persona"), data.get("style"))
            
            self._send_json({
                "answer": answer,
                "action": "wave",
                "data_source": kg.get_data_source_info()
            })
        
        elif parsed.path == "/api/generate-video":
            logging.info("🎬 处理本地视频请求")
            # 本地视频生成接口（保持不变）
            text = data.get("text", "")
            result = fetch_mapped_video(text)
            self._send_json(result)
        
        elif parsed.path == "/api/generate-video-ai":
            logging.info("🎬 处理 AI 视频生成请求")
            # AI 视频生成接口
            text = data.get("text", "")
            resolution = data.get("resolution", "1080p")
            duration = data.get("duration", 10)
            aspect_ratio = data.get("aspect_ratio", "16:9")
            
            if not SEEDANCE_AVAILABLE:
                # SeeDance 不可用，降级到本地视频
                logging.warning("⚠️ SeeDance 不可用，降级到本地视频")
                result = fetch_mapped_video(text)
                result["fallback"] = True
                result["fallback_reason"] = "SeeDance API 不可用"
                self._send_json(result)
                return
            
            try:
                # 调用 SeeDance 生成器
                result = seedance_generator.generate_video(
                    prompt=text,
                    resolution=resolution,
                    duration=duration,
                    aspect_ratio=aspect_ratio,
                    use_cache=True
                )
                self._send_json(result)
                
            except Exception as e:
                logging.error(f"❌ AI 视频生成失败: {e}")
                # 降级到本地视频
                result = fetch_mapped_video(text)
                result["fallback"] = True
                result["fallback_reason"] = f"AI 生成失败: {str(e)}"
                self._send_json(result)
        
        elif parsed.path == "/api/compare-relics":
            logging.info("🔍 处理文物对比请求")
            # 文物对比接口
            relic_a = data.get("relic_a")
            relic_b = data.get("relic_b")
            
            if not relic_a or not relic_b:
                self._send_json({"error": "缺少文物ID"}, 400)
                return
            
            result = kg.compare_relics(relic_a, relic_b)
            self._send_json(result)
        
        else:
            logging.warning(f"❌ 未知路径: {parsed.path}")
            self.send_error(404)

def run_server():
    server_address = ('', PORT)
    httpd = ThreadingHTTPServer(server_address, EnhancedServerHandler)
    
    print("=" * 70)
    print(f"🚀 服务器已启动: http://localhost:{PORT}")
    
    # 显示语音服务状态
    voice_services = []
    if edge_tts_service.available:
        voice_services.append("Edge TTS")
    voice_services.append("浏览器语音")
    
    print(f"🎤 可用语音服务: {' | '.join(voice_services)}")
    
    if edge_tts_service.available:
        print(f"✅ Edge TTS自然语音已启用")
    else:
        print(f"💡 提示: 运行 'pip install edge-tts' 启用Edge TTS")
    
    print(f"🗄️ 知识图谱: {'Neo4j已连接' if kg.connected else '静态模式'}")
    print("=" * 70)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run_server()