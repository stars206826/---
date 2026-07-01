# 会说话的文物 🏛️ | Talking Relics

[![GitHub stars](https://img.shields.io/github/stars/stars206826/--v.1.svg?style=social&label=Star)](https://github.com/stars206826/--v.1)
[![GitHub forks](https://img.shields.io/github/forks/stars206826/--v.1.svg?style=social&label=Fork)](https://github.com/stars206826/--v.1)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[中文](#中文) | [English](#english)

---

<a name="中文"></a>

# 中文文档

> 基于AI技术的智能文化遗产展示系统，让文物"开口说话"

## 🎯 项目简介

**会说话的文物**是一个创新的文化遗产数字化展示平台，通过人工智能技术让古老的文物获得"生命"，能够与观众进行个性化对话交流。系统集成了大语言模型(LLM)、知识图谱、视频生成等前沿技术，为用户提供沉浸式的文化体验。

## ✨ 核心特性

- 🤖 **AI文物对话** - 基于DeepSeek/Qwen模型的智能对话系统
- 🗄️ **Neo4j知识图谱** - 丰富的语义关系网络，支持智能推理和关联查询
- 🎤 **语音交互** - 支持语音输入问题和语音播放回答，真正的语音对话体验
- 🎭 **角色扮演** - 文物第一人称叙述，生动还原历史场景
- 👥 **个性化体验** - 针对儿童、学者、游客提供不同的解说风格
- 🔗 **关联推理** - 基于知识图谱的跨文物关系分析
- 🎬 **视频展示** - 文物制作过程视频，多种格式支持
- 🌐 **全息展示** - 赛博朋克风格的Web界面设计
- 📱 **移动端适配** - 响应式设计，完美支持手机和平板

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 现代浏览器 (Chrome/Firefox/Safari)
- 网络连接 (用于AI API调用)
- Neo4j 数据库（可选，用于知识图谱增强功能）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/stars206826/--v.1.git
cd --v.1
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

### 快速启动

```bash
# Windows 用户
start.bat

# Linux/macOS 用户
./start.sh

# 或手动启动
python enhanced_backend_with_edge_tts.py
```

3. **访问系统**
```
浏览器打开: http://localhost:8000
```

### 配置（可选）

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件填入配置
# - SILICONFLOW_KEY: 在 https://siliconflow.cn 注册获取
# - NEO4J_*: Neo4j 数据库配置（可选）
```

## 🎮 使用指南

### 文物对话
1. 在左侧选择感兴趣的文物
2. 选择观众类型（儿童/学者/游客）和对话模式
3. 输入问题或使用语音输入
4. 享受与文物的智能对话

### 视频展示
1. 切换到"视频生成"页面
2. 输入文物关键词
3. 系统自动播放对应的制作过程视频

## 🛠️ 技术架构

### 后端技术
- **Python** - 核心开发语言
- **HTTP Server** - 轻量级Web服务
- **SiliconFlow API** - AI对话引擎
- **Neo4j** - 图数据库（可选）

### 前端技术
- **HTML5/CSS3** - 现代Web标准
- **JavaScript** - 交互逻辑
- **响应式设计** - 多设备适配

### AI技术
- **大语言模型** - DeepSeek-V3 / Qwen2.5
- **知识图谱** - Neo4j图数据库
- **语音合成** - Edge TTS
- **智能推理** - 基于图结构的关联分析

## 📊 项目数据

- 💻 代码行数: 10,000+ 行
- 🏛️ 文物数量: 6 个（可扩展）
- 🎬 视频资源: 14 个文件（23MB）
- 🖼️ 图片资源: 6 个文件（5MB）
- 🧪 测试用例: 6 个测试类
- 📚 文档数量: 3 个核心文档
- 📜 开源协议: MIT

## 👥 项目团队

### 项目负责人
- **陈浩** - Team Leader
- **张铭泽** - Core Leader  
- **祁美文** - Core Leader

### 核心开发团队
- **周川力** - 核心开发
- **孟祥雨** - 核心开发

### 团队成员
李沁珊、程小芸、苏芯、刘海燕、孙志一、韦敦忆、雷千、但宜珊

## 🤝 贡献指南

欢迎所有形式的贡献！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🔗 相关链接

- [SiliconFlow API](https://siliconflow.cn/) - AI对话服务
- [项目文档](运行说明文档.md) - 详细使用说明

## 🌟 Star History

如果这个项目对你有帮助，请给我们一个 Star！⭐

---

<a name="english"></a>

# English Documentation

> An AI-powered intelligent cultural heritage exhibition system that brings relics to life

## 🎯 Project Overview

**Talking Relics** is an innovative digital platform for cultural heritage exhibition. Using artificial intelligence technology, it gives ancient relics a "voice" to interact with visitors in personalized conversations. The system integrates cutting-edge technologies including Large Language Models (LLM), Knowledge Graphs, and video generation to provide an immersive cultural experience.

## ✨ Key Features

- 🤖 **AI Relic Dialogue** - Intelligent conversation system based on DeepSeek/Qwen models
- 🗄️ **Neo4j Knowledge Graph** - Rich semantic relationship network supporting intelligent reasoning
- 🎤 **Voice Interaction** - Support for voice input and audio output for complete voice dialogue
- 🎭 **Role Playing** - First-person narration from relics, vividly recreating historical scenes
- 👥 **Personalized Experience** - Different explanation styles for children, scholars, and tourists
- 🔗 **Associative Reasoning** - Cross-relic relationship analysis based on knowledge graphs
- 🎬 **Video Display** - Manufacturing process videos with multiple format support
- 🌐 **Holographic Display** - Cyberpunk-style web interface design
- 📱 **Mobile Adaptation** - Responsive design perfectly supporting phones and tablets

## 🚀 Quick Start

### Requirements

- Python 3.8+
- Modern browser (Chrome/Firefox/Safari)
- Internet connection (for AI API calls)
- Neo4j database (optional, for enhanced knowledge graph features)

### Installation

1. **Clone the project**
```bash
git clone https://github.com/stars206826/--v.1.git
cd --v.1
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Quick Launch

```bash
# Windows users
start.bat

# Linux/macOS users
./start.sh

# Or manual start
python enhanced_backend_with_edge_tts.py
```

3. **Access the system**
```
Open in browser: http://localhost:8000
```

### Configuration (Optional)

```bash
# Copy environment variable template
cp .env.example .env

# Edit .env file with your configuration
# - SILICONFLOW_KEY: Register at https://siliconflow.cn
# - NEO4J_*: Neo4j database configuration (optional)
```

## 🎮 User Guide

### Relic Dialogue
1. Select a relic from the left panel
2. Choose audience type (children/scholar/tourist) and dialogue mode
3. Input questions or use voice input
4. Enjoy intelligent conversation with the relic

### Video Display
1. Switch to "Video Generation" page
2. Enter relic keywords
3. System automatically plays corresponding manufacturing process video

## 🛠️ Technical Architecture

### Backend Technology
- **Python** - Core development language
- **HTTP Server** - Lightweight web service
- **SiliconFlow API** - AI dialogue engine
- **Neo4j** - Graph database (optional)

### Frontend Technology
- **HTML5/CSS3** - Modern web standards
- **JavaScript** - Interactive logic
- **Responsive Design** - Multi-device adaptation

### AI Technology
- **Large Language Models** - DeepSeek-V3 / Qwen2.5
- **Knowledge Graph** - Neo4j graph database
- **Voice Synthesis** - Edge TTS
- **Intelligent Reasoning** - Graph-based associative analysis

## 📊 Project Statistics

- 💻 Lines of Code: 10,000+
- 🏛️ Number of Relics: 6 (expandable)
- 🎬 Video Resources: 14 files (23MB)
- 🖼️ Image Resources: 6 files (5MB)
- 🧪 Test Cases: 6 test classes
- 📚 Documentation: 3 core documents
- 📜 License: MIT

## 👥 Project Team

### Project Leaders
- **Chen Hao** - Team Leader
- **Zhang Mingze** - Core Leader  
- **Qi Meiwen** - Core Leader

### Core Development Team
- **Zhou Chuanli** - Core Developer
- **Meng Xiangyu** - Core Developer

### Team Members
Li Qinshan, Cheng Xiaoyun, Su Xin, Liu Haiyan, Sun Zhiyi, Wei Dunyi, Lei Qian, Dan Yishan

## 🤝 Contributing

We welcome all forms of contributions!

1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🔗 Related Links

- [SiliconFlow API](https://siliconflow.cn/) - AI dialogue service
- [Project Documentation](运行说明文档.md) - Detailed usage guide

## 🌟 Star History

If this project helps you, please give us a Star! ⭐

---

**Let technology empower cultural heritage, bringing relics to life in the digital age!**

**让科技为文化传承赋能，让文物在数字时代重新"活"起来！**
