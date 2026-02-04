# Implementation Plan: 豆包语音集成

## Overview

本实现计划将豆包语音服务集成到现有的AI对话系统中。采用最小侵入性的方式，在现有Edge TTS服务基础上添加豆包TTS作为可选的语音合成服务。所有现有功能保持不变，新功能可以通过配置启用/禁用。

**当前状态**：系统已完整实现Edge TTS语音服务，豆包语音服务尚未开始实现。

## Tasks

- [x] 1. 创建豆包语音服务核心类
  - 创建 `doubao_tts_integration.py` 文件
  - 实现 `DoubaoTTSService` 类，保持与 `EdgeTTSService` 相同的接口
  - 实现同步和异步语音合成方法
  - 实现语音配置映射（persona/style -> 豆包发音人参数）
  - 实现火山引擎TTS API请求构建
  - 处理base64编码的音频数据响应
  - _Requirements: 1.1, 2.1, 3.2_

- [ ]* 1.1 编写豆包服务单元测试
  - 测试API请求构建的正确性
  - 测试语音配置映射
  - 测试错误处理逻辑
  - _Requirements: 2.1, 2.4_

- [ ] 2. 实现错误处理和重试机制
  - [x] 2.1 实现HTTP请求超时控制
    - 设置30秒超时限制
    - 处理超时异常
    - 记录超时日志
    - _Requirements: 2.3_

  - [x] 2.2 实现重试机制
    - 网络错误时自动重试，最多3次
    - 实现指数退避策略（1秒、2秒、4秒）
    - 记录每次重试的详细日志
    - _Requirements: 2.2_

  - [x] 2.3 实现错误分类处理
    - 认证错误（401）：提示检查API密钥
    - 请求限制（429）：实现退避重试
    - 服务不可用（503）：触发降级机制
    - 网络超时：记录并重试
    - _Requirements: 2.1, 2.4_

  - [ ]* 2.4 编写API调用属性测试
    - **Property 1: 语音合成触发正确性**
    - **Validates: Requirements 1.1**
    - 测试各种文本输入的API调用正确性

  - [ ]* 2.5 编写重试机制属性测试
    - **Property 6: 重试机制限制性**
    - **Validates: Requirements 2.2**
    - 测试重试次数严格限制在3次以内

  - [ ]* 2.6 编写超时机制属性测试
    - **Property 7: 超时机制准确性**
    - **Validates: Requirements 2.3**
    - 测试30秒超时的准确性

- [ ] 3. 集成到现有后端服务器
  - [x] 3.1 扩展配置管理
    - 在 `enhanced_backend_with_edge_tts.py` 中添加豆包配置字典
    - 从环境变量读取 `DOUBAO_APP_KEY` 和 `DOUBAO_TOKEN`
    - 添加 `DOUBAO_ENABLED` 开关（默认False）
    - 添加 `DOUBAO_API_URL` 配置
    - _Requirements: 2.4, 4.1_

  - [x] 3.2 初始化豆包服务
    - 在服务器启动时初始化 `DoubaoTTSService` 实例
    - 验证API配置的有效性（检查密钥是否为空）
    - 记录服务初始化状态到日志
    - 处理初始化失败的情况
    - _Requirements: 2.4_

  - [x] 3.3 添加豆包语音合成API端点（流式返回）
    - 在 `do_POST` 方法中实现 `POST /api/doubao-synthesize` 接口
    - 保持与现有 `/api/synthesize-speech` 相同的请求格式
    - 调用 `DoubaoTTSService.synthesize_speech()` 方法
    - **直接返回音频数据流（不保存文件）**
    - 返回 `audio/mpeg` 类型的响应
    - _Requirements: 1.1, 1.2_

  - [ ]* 3.4 编写API端点集成测试
    - 测试端点的请求处理
    - 测试音频流返回
    - 测试错误响应格式
    - _Requirements: 1.1, 2.1_

- [ ] 4. 实现服务降级机制
  - [x] 4.1 实现降级逻辑
    - 豆包API调用失败时自动降级到Edge TTS
    - 记录降级事件到日志
    - 在响应中返回降级状态标志
    - 在 `/api/doubao-synthesize` 端点中实现降级
    - _Requirements: 4.2_

  - [ ]* 4.2 编写错误处理属性测试
    - **Property 5: 错误处理完整性**
    - **Validates: Requirements 2.1**
    - 测试各种错误情况的处理正确性

- [ ] 5. Checkpoint - 后端核心功能验证
  - 确保豆包服务类可以正常实例化
  - 手动测试豆包API调用（使用真实API密钥）
  - 验证降级机制工作正常
  - 验证音频文件正确保存
  - 询问用户是否有问题

- [ ] 6. 扩展语音服务状态API
  - [x] 6.1 更新 `/api/speech-status` 接口
    - 添加 `doubao_available` 状态字段
    - 添加 `available_services` 列表（包含edge_tts、doubao、browser）
    - 添加 `current_service` 字段显示当前使用的服务
    - 更新 `message` 字段以反映多服务状态
    - _Requirements: 4.2_

  - [ ] 6.2 实现服务切换接口（可选）
    - 实现 `POST /api/voice-service-switch` 接口
    - 接收 `service` 参数（edge_tts/doubao）
    - 验证切换请求的有效性
    - 更新全局服务配置
    - _Requirements: 4.2_

  - [ ]* 6.3 编写服务切换属性测试
    - **Property 12: 服务切换无缝性**
    - **Validates: Requirements 4.2**
    - 测试服务切换不影响正在进行的操作

- [ ] 7. 实现日志和监控
  - [x] 7.1 添加豆包服务日志
    - 记录每次API调用的详细信息（时间戳、文本长度、persona、style）
    - 记录请求时间和响应时间
    - 记录使用的发音人和参数
    - 使用 `logging.info()` 记录成功调用
    - _Requirements: 5.1_

  - [x] 7.2 添加错误日志
    - 记录所有错误的详细信息
    - 记录错误类型、错误消息、时间戳
    - 记录API响应的完整内容（状态码、响应体）
    - 使用 `logging.error()` 记录错误
    - _Requirements: 5.2_

  - [x] 7.3 添加性能监控
    - 记录响应时间超过5秒的请求
    - 在日志中标记慢请求
    - 记录降级事件的频率
    - _Requirements: 5.4_

  - [ ]* 7.4 编写日志记录属性测试
    - **Property 13: 日志记录完整性**
    - **Validates: Requirements 5.1**
    - 测试日志包含所有必要信息

  - [ ]* 7.5 编写错误日志属性测试
    - **Property 14: 错误日志详细性**
    - **Validates: Requirements 5.2**
    - 测试错误日志的完整性

- [ ] 8. 前端集成（可选扩展）
  - [ ] 8.1 添加语音服务选择UI
    - 在 `enhanced_frontend.html` 中添加服务选择下拉菜单
    - 显示当前可用的语音服务（从 `/api/speech-status` 获取）
    - 保存用户选择到 `localStorage`
    - 添加服务状态指示器
    - _Requirements: 3.1, 3.3_

  - [x] 8.2 更新语音播放逻辑（流式播放）
    - 根据用户选择调用对应的API端点（优先 `/api/doubao-synthesize`）
    - **使用Blob URL实现实时播放（不保存文件）**
    - 显示当前使用的语音服务名称
    - 处理服务切换的UI反馈
    - 显示降级提示（如果发生降级）
    - 播放完成后自动释放Blob URL资源
    - _Requirements: 1.2, 1.3_

  - [ ]* 8.3 编写前端集成测试
    - 测试服务选择功能
    - 测试设置持久化
    - 测试播放状态显示
    - _Requirements: 1.3, 3.3, 3.4_

- [ ] 9. 更新配置文档
  - [x] 9.1 更新 `.env.example` 文件
    - 添加 `DOUBAO_APP_KEY` 配置项
    - 添加 `DOUBAO_TOKEN` 配置项
    - 添加 `DOUBAO_ENABLED` 配置项（默认false）
    - 添加配置说明注释
    - _Requirements: 2.4_

  - [x] 9.2 创建豆包配置指南
    - 创建 `豆包语音服务配置指南.md` 文件
    - 说明如何在火山引擎获取API密钥
    - 说明如何配置环境变量
    - 提供配置示例和故障排除
    - _Requirements: 2.4_

  - [x] 9.3 更新README文档
    - 在"语音交互功能"部分添加豆包语音服务说明
    - 更新安装步骤（添加豆包配置）
    - 添加豆包服务的特性说明
    - 添加故障排除指南
    - _Requirements: 2.4_

- [ ] 10. 最终测试和验证
  - [x] 10.1 端到端测试
    - 测试完整的语音合成流程（从前端到后端）
    - 测试服务降级场景（模拟豆包API失败）
    - 测试错误处理场景（无效密钥、网络超时等）
    - 测试音频播放功能
    - _Requirements: 1.1, 1.2, 2.1, 4.2_

  - [ ]* 10.2 编写播放控制属性测试
    - **Property 2: 语音播放自动启动**
    - **Validates: Requirements 1.2**
    - **Property 4: 停止操作即时性**
    - **Validates: Requirements 1.4**

  - [ ]* 10.3 编写接口兼容性属性测试
    - **Property 11: 接口兼容性保持**
    - **Validates: Requirements 4.1**
    - 测试新服务与现有接口的兼容性

- [ ] 11. Final Checkpoint - 完整验证
  - 确保所有核心功能测试通过
  - 验证现有Edge TTS功能未受影响
  - 验证豆包服务可以正常启用/禁用
  - 验证降级机制在各种场景下正常工作
  - 询问用户是否满意，是否需要调整

## Notes

- 任务标记 `*` 的为可选测试任务，可以跳过以加快MVP开发
- 每个任务都引用了具体的需求编号，确保可追溯性
- Checkpoint任务确保增量验证，及时发现问题
- 属性测试验证通用正确性属性
- 单元测试验证具体示例和边界情况
- 所有新增代码都应该保持与现有代码风格一致
- 豆包服务默认禁用，需要手动配置启用
- 现有Edge TTS功能完全不受影响
- 豆包API文档：https://www.volcengine.com/docs/6561/79820