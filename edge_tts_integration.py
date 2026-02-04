#!/usr/bin/env python3
"""
Edge TTS语音合成集成
免费且自然的语音合成解决方案
"""

import asyncio
import edge_tts
import os
import tempfile
import hashlib
import json
from typing import Dict, Optional

class EdgeTTSService:
    def __init__(self):
        """初始化Edge TTS服务"""
        self.available = True
        try:
            # 测试edge_tts是否可用
            import edge_tts
            print("✅ Edge TTS服务可用")
        except ImportError:
            self.available = False
            print("❌ Edge TTS未安装，请运行: pip install edge-tts")
    
    def get_voice_config(self, persona: str, style: str) -> Dict[str, str]:
        """
        根据角色和风格选择最佳语音配置
        
        Args:
            persona: 角色类型 (child/scholar/tourist)
            style: 风格类型 (personified/guide)
            
        Returns:
            包含语音名称和参数的字典
        """
        voice_configs = {
            'child': {
                'voice': 'zh-CN-XiaoxiaoNeural',  # 温柔女声，适合儿童
                'rate': '-20%',  # 稍慢
                'pitch': '+10Hz',  # 音调稍高
                'volume': '+0%'  # 标准音量
            },
            'scholar': {
                'voice': 'zh-CN-YunxiNeural',  # 成熟男声，适合学者
                'rate': '-30%',  # 很慢
                'pitch': '-10Hz',  # 音调稍低
                'volume': '-10%'  # 音量稍小
            },
            'tourist': {
                'voice': 'zh-CN-XiaoyiNeural',  # 活泼女声，适合游客
                'rate': '-10%',  # 稍慢
                'pitch': '+5Hz',  # 音调稍高
                'volume': '+5%'  # 音量稍大
            }
        }
        
        config = voice_configs.get(persona, voice_configs['tourist'])
        
        # 拟人化风格的调整
        if style == 'personified':
            # 增加个性化
            current_pitch = int(config['pitch'].replace('Hz', '').replace('+', '').replace('-', ''))
            config['pitch'] = f"+{current_pitch + 5}Hz"
            
            # 语速稍快一点
            current_rate = int(config['rate'].replace('%', '').replace('+', '').replace('-', ''))
            config['rate'] = f"{current_rate + 5}%"
        
        return config
    
    def create_ssml(self, text: str, persona: str, style: str) -> str:
        """
        创建SSML标记语言，实现更自然的语音效果
        
        Args:
            text: 要合成的文本
            persona: 角色类型
            style: 风格类型
            
        Returns:
            SSML格式的文本
        """
        config = self.get_voice_config(persona, style)
        
        # 处理文本中的情感标记
        processed_text = self.process_emotional_text(text)
        
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
    
    def process_emotional_text(self, text: str) -> str:
        """
        处理文本中的情感表达，添加SSML标记
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        # 为感叹句添加强调
        text = text.replace('！', '<emphasis level="strong">！</emphasis>')
        text = text.replace('!', '<emphasis level="strong">!</emphasis>')
        
        # 为省略号添加停顿
        text = text.replace('...', '<break time="800ms"/>')
        text = text.replace('…', '<break time="800ms"/>')
        
        # 为问号添加疑问语调
        text = text.replace('？', '<prosody pitch="+15%">？</prosody>')
        text = text.replace('?', '<prosody pitch="+15%">?</prosody>')
        
        # 为特定词汇添加情感
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
            text = text.replace(word, replacement)
        
        return text
    
    async def synthesize_speech_async(self, text: str, persona: str = 'tourist', style: str = 'guide') -> Optional[bytes]:
        """
        异步合成语音
        
        Args:
            text: 要合成的文本
            persona: 角色类型
            style: 风格类型
            
        Returns:
            音频数据（MP3格式）或None（如果失败）
        """
        if not self.available:
            return None
        
        try:
            # 创建SSML
            ssml = self.create_ssml(text, persona, style)
            
            # 使用Edge TTS合成语音
            config = self.get_voice_config(persona, style)
            communicate = edge_tts.Communicate(ssml, config['voice'])
            
            # 收集音频数据
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            return audio_data
            
        except Exception as e:
            print(f"Edge TTS语音合成异常: {e}")
            return None
    
    def synthesize_speech(self, text: str, persona: str = 'tourist', style: str = 'guide') -> Optional[bytes]:
        """
        同步合成语音（包装异步方法）
        
        Args:
            text: 要合成的文本
            persona: 角色类型
            style: 风格类型
            
        Returns:
            音频数据（MP3格式）或None（如果失败）
        """
        try:
            # 创建新的事件循环或使用现有的
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(
                self.synthesize_speech_async(text, persona, style)
            )
        except Exception as e:
            print(f"语音合成失败: {e}")
            return None
    
    def synthesize_to_file(self, text: str, output_file: str, persona: str = 'tourist', style: str = 'guide') -> bool:
        """
        合成语音并保存到文件
        
        Args:
            text: 要合成的文本
            output_file: 输出文件路径
            persona: 角色类型
            style: 风格类型
            
        Returns:
            是否成功
        """
        audio_data = self.synthesize_speech(text, persona, style)
        if audio_data:
            try:
                with open(output_file, 'wb') as f:
                    f.write(audio_data)
                return True
            except Exception as e:
                print(f"保存文件失败: {e}")
                return False
        return False

# 获取可用的Edge TTS语音列表
async def get_available_voices():
    """获取可用的Edge TTS语音列表"""
    try:
        voices = await edge_tts.list_voices()
        chinese_voices = [v for v in voices if 'zh-CN' in v['Locale']]
        return chinese_voices
    except Exception as e:
        print(f"获取语音列表失败: {e}")
        return []

# 测试函数
def test_edge_tts():
    """测试Edge TTS服务"""
    
    print("🎤 Edge TTS语音合成测试")
    print("=" * 50)
    
    # 创建语音服务实例
    tts_service = EdgeTTSService()
    
    if not tts_service.available:
        print("❌ Edge TTS不可用，请先安装：pip install edge-tts")
        return
    
    # 测试文本
    test_texts = {
        'child': "哇！小朋友你好呀！我是一个超级神奇的青铜鼎哦～你知道吗？我已经两千多岁啦！",
        'scholar': "嗯...从考古学角度来看，我这件巴渝青铜祭祀鼎，实际上呢...代表了战国晚期的工艺水平。",
        'tourist': "朋友们！您知道吗？我可是这里的明星文物呢！猜猜看，我是怎么制作出来的？"
    }
    
    # 为每种角色生成语音
    for persona, text in test_texts.items():
        print(f"\n🎭 正在生成{persona}模式语音...")
        output_file = f"edge_tts_{persona}.mp3"
        
        success = tts_service.synthesize_to_file(
            text=text,
            output_file=output_file,
            persona=persona,
            style='personified'
        )
        
        if success:
            print(f"✅ {persona}模式语音已保存到: {output_file}")
        else:
            print(f"❌ {persona}模式语音生成失败")
    
    print(f"\n{'='*50}")
    print("🎉 测试完成！请播放生成的MP3文件听取效果")

# 获取语音列表的测试函数
async def test_voice_list():
    """测试获取语音列表"""
    print("📋 获取Edge TTS中文语音列表...")
    voices = await get_available_voices()
    
    print(f"\n🎤 找到 {len(voices)} 个中文语音：")
    for i, voice in enumerate(voices, 1):
        gender = voice.get('Gender', '未知')
        name = voice.get('ShortName', voice.get('Name', '未知'))
        print(f"{i:2d}. {name} ({gender})")

if __name__ == "__main__":
    # 运行测试
    test_edge_tts()
    
    # 获取语音列表
    print("\n" + "="*50)
    asyncio.run(test_voice_list())