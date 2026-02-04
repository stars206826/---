# Neo4j知识图谱配置指南

## 📋 概述

本指南将帮助你配置Neo4j数据库，以启用"会说话的文物"系统的完整知识图谱功能。Neo4j是一个高性能的图数据库，能够存储和查询复杂的关系数据。

## 🎯 为什么使用Neo4j？

### 传统方式 vs Neo4j增强
| 功能 | 静态知识库 | Neo4j知识图谱 |
|------|------------|---------------|
| 文物信息查询 | ✅ 基础信息 | ✅ 丰富的结构化信息 |
| 关联文物发现 | ❌ 无法关联 | ✅ 智能关联推荐 |
| 历史背景分析 | ❌ 静态描述 | ✅ 动态上下文分析 |
| 跨文物对比 | ❌ 无法对比 | ✅ 多维度对比分析 |
| 知识扩展 | ❌ 需要修改代码 | ✅ 动态添加数据 |

### AI回答质量提升
使用Neo4j后，AI能够：
- 🔍 **智能关联**: "这个青铜鼎和同时期的其他文物有什么关系？"
- 📍 **地理分析**: "巴渝地区还有哪些重要的文物？"
- ⏰ **时代对比**: "战国时期的工艺水平如何？"
- 🎨 **工艺传承**: "这种制作工艺影响了后世哪些文物？"

## 🚀 安装方法

### 方法一：Neo4j Desktop（推荐新手）

1. **下载Neo4j Desktop**
   - 访问 [Neo4j官网](https://neo4j.com/download/)
   - 选择"Neo4j Desktop"
   - 填写信息获取激活密钥（免费）

2. **安装和配置**
   ```
   1. 运行下载的安装程序
   2. 输入激活密钥
   3. 创建新项目："会说话的文物"
   4. 添加本地数据库
   5. 设置数据库名称：talking-relics
   6. 设置密码：12345678
   7. 启动数据库
   ```

3. **验证安装**
   - 打开Neo4j Browser: `http://localhost:7474`
   - 使用用户名：`neo4j`，密码：`12345678` 登录
   - 运行测试查询：`RETURN "Hello Neo4j!"`

### 方法二：Docker（推荐开发者）

1. **安装Docker**
   - Windows: 下载Docker Desktop
   - macOS: 下载Docker Desktop
   - Linux: `sudo apt-get install docker.io`

2. **运行Neo4j容器**
   ```bash
   # 创建数据目录
   mkdir -p $HOME/neo4j/data
   mkdir -p $HOME/neo4j/logs
   mkdir -p $HOME/neo4j/import
   mkdir -p $HOME/neo4j/plugins

   # 启动Neo4j容器
   docker run \
       --name talking-relics-neo4j \
       -p7474:7474 -p7687:7687 \
       -d \
       -v $HOME/neo4j/data:/data \
       -v $HOME/neo4j/logs:/logs \
       -v $HOME/neo4j/import:/var/lib/neo4j/import \
       -v $HOME/neo4j/plugins:/plugins \
       --env NEO4J_AUTH=neo4j/12345678 \
       --env NEO4J_PLUGINS='["apoc"]' \
       neo4j:5.15
   ```

3. **验证安装**
   ```bash
   # 检查容器状态
   docker ps

   # 查看日志
   docker logs talking-relics-neo4j

   # 访问Neo4j Browser
   # http://localhost:7474
   ```

### 方法三：系统安装（Linux/macOS）

1. **Ubuntu/Debian**
   ```bash
   # 添加Neo4j仓库
   wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
   echo 'deb https://debian.neo4j.com stable latest' | sudo tee -a /etc/apt/sources.list.d/neo4j.list
   sudo apt-get update

   # 安装Neo4j
   sudo apt-get install neo4j

   # 设置密码
   sudo neo4j-admin set-initial-password 12345678

   # 启动服务
   sudo systemctl enable neo4j
   sudo systemctl start neo4j
   ```

2. **macOS (Homebrew)**
   ```bash
   # 安装Neo4j
   brew install neo4j

   # 启动Neo4j
   neo4j start

   # 设置密码（首次访问时在浏览器中设置）
   ```

## ⚙️ 配置系统连接

### 1. 检查连接参数
确保以下配置正确：
```python
# 在 integrated_backend_neo4j.py 中
NEO4J_URI = "bolt://localhost:7687"  # Neo4j连接地址
NEO4J_USER = "neo4j"                 # 用户名
NEO4J_PASSWORD = "12345678"          # 密码
```

### 2. 测试连接
```bash
# 启动Neo4j增强版服务器
python integrated_backend_neo4j.py

# 查看启动日志
# 成功：✅ Neo4j数据库连接成功
# 失败：⚠️ Neo4j连接失败: [错误信息]
```

### 3. 验证数据初始化
启动成功后，系统会自动创建知识图谱数据：
```
🗄️ Neo4j知识图谱数据初始化完成
```

## 🔍 验证知识图谱功能

### 1. 在Neo4j Browser中查看数据
访问 `http://localhost:7474`，运行以下查询：

```cypher
// 查看所有文物
MATCH (a:Artifact) RETURN a

// 查看文物关系网络
MATCH (a:Artifact)-[r]->(b) RETURN a, r, b

// 查看特定文物的关联
MATCH (a:Artifact {name: "巴渝青铜祭祀鼎"})-[r]->(b) RETURN a, r, b
```

### 2. 测试AI对话增强功能
在系统中尝试以下问题：

**基础问题**：
- "请介绍一下自己"
- "你是什么时候制作的？"

**关联问题**（Neo4j增强）：
- "和你同时期的文物还有哪些？"
- "你们这个地区有什么文化特色？"
- "你和其他文物有什么关系？"

### 3. API接口测试
```bash
# 测试知识图谱API
curl http://localhost:8000/api/knowledge-graph

# 应该返回包含nodes和edges的JSON数据
```

## 🛠️ 故障排除

### 常见问题

**1. 连接被拒绝**
```
Neo4j连接失败: Failed to establish connection
```
**解决方案**：
- 检查Neo4j服务是否启动
- 确认端口7687未被占用
- 验证用户名密码是否正确

**2. 认证失败**
```
Neo4j连接失败: Authentication failure
```
**解决方案**：
- 重置Neo4j密码：`neo4j-admin set-initial-password 12345678`
- 或在代码中修改密码配置

**3. 端口冲突**
```
Neo4j连接失败: Connection refused
```
**解决方案**：
- 检查端口占用：`netstat -an | grep 7687`
- 修改Neo4j配置文件中的端口设置

**4. Docker容器问题**
```bash
# 重启容器
docker restart talking-relics-neo4j

# 查看详细日志
docker logs -f talking-relics-neo4j

# 重新创建容器
docker rm -f talking-relics-neo4j
# 然后重新运行docker run命令
```

### 性能优化

**1. 内存配置**
```bash
# 在Neo4j配置文件中调整内存
dbms.memory.heap.initial_size=512m
dbms.memory.heap.max_size=1G
dbms.memory.pagecache.size=512m
```

**2. 索引优化**
```cypher
// 为常用查询创建索引
CREATE INDEX artifact_name FOR (a:Artifact) ON (a.name)
CREATE INDEX artifact_era FOR (a:Artifact) ON (a.era)
CREATE INDEX artifact_category FOR (a:Artifact) ON (a.category)
```

## 📈 扩展知识图谱

### 添加新文物
```cypher
// 创建新文物节点
CREATE (a:Artifact {
    id: "new_artifact_id",
    name: "新文物名称",
    era: "历史时期",
    category: "文物类别",
    location: "地理位置",
    summary: "文物描述",
    story: "文物故事"
})

// 建立关系
MATCH (a:Artifact {id: "new_artifact_id"}), (e:Era {name: "历史时期"})
CREATE (a)-[:BELONGS_TO_ERA]->(e)
```

### 添加新关系类型
```cypher
// 创建影响关系
MATCH (a1:Artifact {name: "文物A"}), (a2:Artifact {name: "文物B"})
CREATE (a1)-[:INFLUENCES]->(a2)

// 创建相似关系
MATCH (a1:Artifact {name: "文物A"}), (a2:Artifact {name: "文物B"})
CREATE (a1)-[:SIMILAR_TO]->(a2)
```

## 🎯 最佳实践

1. **定期备份数据**
   ```bash
   # 导出数据
   neo4j-admin dump --database=neo4j --to=/path/to/backup.dump
   
   # 恢复数据
   neo4j-admin load --from=/path/to/backup.dump --database=neo4j --force
   ```

2. **监控性能**
   - 使用Neo4j Browser的查询分析器
   - 监控慢查询日志
   - 定期检查数据库统计信息

3. **安全配置**
   - 修改默认密码
   - 配置防火墙规则
   - 启用SSL加密（生产环境）

## 🔗 相关资源

- [Neo4j官方文档](https://neo4j.com/docs/)
- [Cypher查询语言指南](https://neo4j.com/docs/cypher-manual/current/)
- [Neo4j Python驱动文档](https://neo4j.com/docs/python-manual/current/)
- [图数据库最佳实践](https://neo4j.com/developer/guide-data-modeling/)

---

通过以上配置，你的"会说话的文物"系统将具备强大的知识图谱能力，AI回答将更加智能和丰富！🚀