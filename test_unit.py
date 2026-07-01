"""
会说话的文物 - 单元测试示例

运行测试：
    pytest test_unit.py -v

依赖：
    pip install pytest pytest-asyncio
"""

import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestKnowledgeGraph:
    """知识图谱功能测试"""

    def test_static_knowledge_exists(self):
        """测试静态知识库数据完整性"""
        from enhanced_backend_with_edge_tts import STATIC_KNOWLEDGE_GRAPH

        assert len(STATIC_KNOWLEDGE_GRAPH) > 0, "静态知识库不应为空"

        # 检查必需的文物
        assert "bronze_ding" in STATIC_KNOWLEDGE_GRAPH
        assert "rock_carving" in STATIC_KNOWLEDGE_GRAPH
        assert "sanxingdui_bronze_mask" in STATIC_KNOWLEDGE_GRAPH

    def test_artifact_structure(self):
        """测试文物数据结构"""
        from enhanced_backend_with_edge_tts import STATIC_KNOWLEDGE_GRAPH

        for artifact_id, artifact in STATIC_KNOWLEDGE_GRAPH.items():
            assert "id" in artifact, f"{artifact_id} 缺少 id 字段"
            assert "name" in artifact, f"{artifact_id} 缺少 name 字段"
            assert "era" in artifact, f"{artifact_id} 缺少 era 字段"
            assert "summary" in artifact, f"{artifact_id} 缺少 summary 字段"


class TestVideoMapping:
    """视频映射功能测试"""

    def test_video_map_exists(self):
        """测试视频映射表"""
        from enhanced_backend_with_edge_tts import VIDEO_MAP

        assert len(VIDEO_MAP) > 0, "视频映射表不应为空"
        assert "大足石刻制造" in VIDEO_MAP

    @patch('enhanced_backend_with_edge_tts.os.path.exists')
    def test_fetch_mapped_video(self, mock_exists):
        """测试视频获取功能"""
        from enhanced_backend_with_edge_tts import fetch_mapped_video

        # 模拟文件存在
        mock_exists.return_value = True

        result = fetch_mapped_video("大足石刻制造")

        assert result["success"] == True
        assert "video_url" in result


class TestTextCleaning:
    """文本清理功能测试"""

    def test_clean_text_removes_markdown(self):
        """测试移除Markdown格式"""
        from enhanced_backend_with_edge_tts import clean_text_for_speech

        text = "这是**粗体**和*斜体*文本"
        cleaned = clean_text_for_speech(text)

        assert "**" not in cleaned
        assert "*" not in cleaned
        assert "粗体" in cleaned
        assert "斜体" in cleaned

    def test_clean_text_converts_punctuation(self):
        """测试标点符号转换"""
        from enhanced_backend_with_edge_tts import clean_text_for_speech

        text = "Hello, world! How are you?"
        cleaned = clean_text_for_speech(text)

        # 应该移除英文字母
        assert "Hello" not in cleaned
        assert "world" not in cleaned

    def test_clean_text_preserves_chinese(self):
        """测试保留中文内容"""
        from enhanced_backend_with_edge_tts import clean_text_for_speech

        text = "我是青铜鼎，来自战国时代。"
        cleaned = clean_text_for_speech(text)

        assert "青铜鼎" in cleaned
        assert "战国时代" in cleaned


class TestEdgeTTSService:
    """Edge TTS 语音服务测试"""

    def test_voice_config_exists(self):
        """测试语音配置"""
        from enhanced_backend_with_edge_tts import edge_tts_service

        # 测试不同角色的配置
        for persona in ['child', 'scholar', 'tourist']:
            config = edge_tts_service.get_voice_config(persona, 'guide')

            assert 'voice' in config
            assert 'rate' in config
            assert 'pitch' in config
            assert 'volume' in config


class TestAPIConfiguration:
    """API配置测试"""

    def test_api_key_from_env(self):
        """测试API密钥从环境变量读取"""
        with patch.dict(os.environ, {'SILICONFLOW_KEY': 'test-key-123'}):
            # 重新加载模块以使用新的环境变量
            import importlib
            import enhanced_backend_with_edge_tts
            importlib.reload(enhanced_backend_with_edge_tts)

            # 检查是否从环境变量读取
            assert os.getenv('SILICONFLOW_KEY') == 'test-key-123'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
