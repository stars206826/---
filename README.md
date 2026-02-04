# 会说话的文物 🏛️

[![GitHub stars](https://img.shields.io/github/stars/stars206826/---.svg?style=social&label=Star)](https://github.com/stars206826/---)
[![GitHub forks](https://img.shields.io/github/forks/stars206826/---.svg?style=social&label=Fork)](https://github.com/stars206826/---)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> 基于AI技术的智能文化遗产展示系统，让文物"开口说话"

## 🎯 项目简介

**会说话的文物**是一个创新的文化遗产数字化展示平台，通过人工智能技术让古老的文物获得"生命"，能够与观众进行个性化对话交流。系统集成了大语言模型(LLM)、知识图谱、视频生成等前沿技术，为用户提供沉浸式的文化体验。

### ✨ 核心特性

- 🤖 **AI文物对话** - 基于DeepSeek/Qwen模型的智能对话系统
- 🗄️ **Neo4j知识图谱** - 丰富的语义关系网络，支持智能推理和关联查询
- 🎤 **语音交互** - 支持语音输入问题和语音播放回答，真正的语音对话体验
- 🎭 **角色扮演** - 文物第一人称叙述，生动还原历史场景
- 👥 **个性化体验** - 针对儿童、学者、游客提供不同的解说风格
- 🔗 **关联推理** - 基于知识图谱的跨文物关系分析
- 🎬 **AI视频生成** - 文本转视频功能，支持多种艺术风格
- 🌐 **全息展示** - 赛博朋克风格的Web界面设计
- 📱 **移动端适配** - 响应式设计，完美支持手机和平板

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 现代浏览器 (Chrome/Firefox/Safari)
- 网络连接 (用于AI API调用)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/stars206826/---.git
cd ---
```

2. **安装依赖**
```bash
# 基础依赖
pip install requests

# Neo4j支持（推荐，用于知识图谱功能）
pip install neo4j
```

3. **安装Neo4j数据库（可选但推荐）**
```bash
# 使用Docker快速启动Neo4j
docker run \
    --name neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    --env NEO4J_AUTH=neo4j/12345678 \
    neo4j:latest

# 或访问 https://neo4j.com/download/ 下载Neo4j Desktop
```

4. **配置环境变量**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥
# 需要在 https://siliconflow.cn 注册获取API密钥
```

5. **启动服务**
```bash
# 标准模式
python integrated_backend2.py

# Neo4j增强模式（推荐）
python integrated_backend_neo4j.py
```

5. **访问系统**
打开浏览器访问: `http://localhost:8000`

### 🗄️ Neo4j知识图谱功能

启用Neo4j后，系统将提供以下增强功能：

- **智能关联查询**: 自动发现文物间的历史、地理、文化关系
- **上下文感知对话**: 根据问题类型提供相关的背景信息
- **跨文物推理**: 比较分析不同时期、地区的文物特征
- **动态知识扩展**: 支持添加新的文物和关系数据
- **可视化支持**: 提供知识图谱数据接口用于可视化展示

### 🎤 语音交互功能

系统支持多种语音合成服务，提供高质量的中文语音体验：

#### 支持的语音服务

1. **豆包语音服务**（推荐）
   - 基于火山引擎TTS API
   - 高质量中文语音合成
   - 支持多种发音人和情感表达
   - 自动重试和降级机制
   - 配置方法：参见[豆包语音服务配置指南.md](豆包语音服务配置指南.md)

2. **Edge TTS**（免费）
   - 微软Edge浏览器的TTS引擎
   - 自然流畅的中文语音
   - 无需API密钥，开箱即用
   - 安装：`pip install edge-tts`

3. **浏览器语音合成**（备用）
   - 使用浏览器内置的Web Speech API
   - 无需额外配置
   - 作为最后的降级方案

#### 语音功能特性

- **智能语音识别**: 中文语音转文字，支持自然语言提问
- **AI语音回答**: 文物回答自动转换为语音播放
- **多模态交互**: 文字、语音、图像的完整交互体验
- **实时状态反馈**: 录音和播放状态的可视化提示
- **自动播放模式**: 可设置AI回答后自动语音播放
- **跨平台支持**: 支持桌面和移动端的语音交互
- **服务降级**: 自动在多个语音服务间切换，确保可用性

#### 语音服务配置

**启用豆包语音服务：**

1. 在火山引擎获取API密钥（参见配置指南）
2. 在 `.env` 文件中配置：
   ```env
   DOUBAO_APP_KEY=your_app_key_here
   DOUBAO_TOKEN=your_access_token_here
   DOUBAO_ENABLED=true
   ```
3. 重启服务器

**启用Edge TTS：**

```bash
pip install edge-tts
```

#### 语音功能测试
访问 `test_voice_features.html` 可以测试浏览器的语音功能兼容性。

## 🌐 外网访问配置

使用cpolar实现外网访问，让其他设备也能使用：

```bash
# 安装cpolar
curl -L https://www.cpolar.com/static/downloads/install-release-cpolar.sh | sudo bash

# 创建隧道
cpolar http 8000

# 获取公网地址，分享给其他人访问
```

详细配置请参考：[运行说明文档.md](运行说明文档.md)

## 📖 功能介绍

### 🏛️ 文物对话系统

系统内置三个经典文物：
- **巴渝青铜祭祀鼎** (战国晚期)
- **大足石刻菩萨造像** (南宋)  
- **三峡古航运木船** (明清时期)

每个文物都有独特的"性格"和历史故事，能够：
- 🗣️ 用第一人称讲述自己的历史
- 🎯 根据观众类型调整语言风格
- 💭 回答关于历史、工艺、文化的问题
- 🎭 展现不同的"情绪"和"动作"

### 🎬 AI视频生成

支持将文本描述转换为动态视频：
- 📝 自然语言输入
- 🎨 多种艺术风格 (写实、动漫、水彩等)
- ⚙️ 可调节参数 (时长、分辨率、帧率)
- 🌈 色彩主题选择
- 💾 视频下载和分享

### 🎨 界面设计

- 🌌 赛博朋克风格的未来感设计
- 🔮 全息投影效果的文物展示
- 📱 完美的移动端适配
- 🎯 直观的用户交互体验

## 🛠️ 技术架构

### 后端技术栈
- **Python** - 核心开发语言
- **HTTP Server** - 轻量级Web服务
- **SiliconFlow API** - AI对话引擎
- **JSON** - 数据交换格式

### 前端技术栈
- **HTML5/CSS3** - 现代Web标准
- **JavaScript** - 交互逻辑
- **响应式设计** - 多设备适配
- **CSS动画** - 流畅的视觉效果

### AI技术
- **大语言模型** - DeepSeek-V3 / Qwen2.5
- **知识图谱** - Neo4j图数据库，语义关系建模
- **智能推理** - 基于图结构的关联分析
- **文本生成** - 个性化内容创作
- **视频生成** - 多模态AI技术

## 📁 项目结构

```
会说话的文物/
├── integrated_backend2.py        # 标准版后端服务器
├── integrated_backend_neo4j.py   # Neo4j增强版后端服务器
├── integrated_frontend.html      # 前端界面
├── 运行说明文档.md               # 详细使用说明
├── .env.example                  # 环境变量模板
├── .gitignore                   # Git忽略文件
├── images/                      # 文物图片资源
│   ├── 1.jpg                   # 青铜鼎
│   ├── 2.jpg                   # 大足石刻
│   └── 3.jpg                   # 古船模型
└── output/                      # 视频输出目录
    ├── 2.mp4                   # 示例视频
    └── ...
```

## 🎮 使用指南

### 1. 文物对话
1. 在左侧选择感兴趣的文物
2. 选择观众类型和对话模式
3. 输入问题或点击"启动对话"
4. 享受与文物的智能对话

### 2. 视频生成
1. 切换到"视频生成"页面
2. 输入想要转换的文本描述
3. 调整视频参数和风格
4. 点击生成按钮等待处理
5. 预览和下载生成的视频

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

我们欢迎所有形式的贡献！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🔗 相关链接

- [SiliconFlow API](https://siliconflow.cn/) - AI对话服务
- [cpolar](https://www.cpolar.com/) - 内网穿透工具
- [项目演示视频](#) - 功能展示

## 📞 联系我们

- 📧 Email: [项目邮箱]
- 🐛 Issues: [GitHub Issues](https://github.com/stars206826/---/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/stars206826/---/discussions)

## 🌟 致谢

感谢所有为这个项目做出贡献的开发者和文化遗产保护工作者！

---

⭐ 如果这个项目对你有帮助，请给我们一个Star！

🎯 让科技为文化传承赋能，让文物在数字时代重新"活"起来！