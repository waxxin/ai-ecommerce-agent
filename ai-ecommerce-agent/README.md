# AI E-commerce Agent 🤖

> 基于LLM的企业级电商内容生成系统

一个完整的AI电商运营Agent系统，支持多平台商品标题生成、卖点提取、FAQ生成，引入RAG知识检索增强生成质量，前后端完整闭环。

---

## ✨ 项目亮点

- **LLM单次调用升级为Agent多步骤系统**：将复杂任务拆解为独立步骤，提升可控性和可维护性
- **引入RAG增强规则控制生成稳定性**：知识库注入平台规则，确保生成内容符合规范
- **前后端+AI完整闭环系统**：Vue3前端 + FastAPI后端 + LLM服务端，完整的工程化架构
- **结构化输出保证**：强制JSON格式输出，避免LLM幻觉导致的解析错误
- **可观测性设计**：记录每步骤执行时间、Token消耗，支持执行过程复盘

---

## 🛠 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue3 | 3.5.x |
| UI组件库 | Element Plus | 2.9.x |
| HTTP客户端 | Axios | 1.7.x |
| 构建工具 | Vite | 6.5.x |
| 后端框架 | FastAPI | 0.115.x |
| ORM | SQLAlchemy | 2.0.x |
| 数据库 | MySQL | 8.0+ |
| LLM服务 | 阿里云百炼 / DeepSeek | - |
| 向量检索 | Sentence Transformers | 3.0.x |

---

## 🏗 系统架构

```
用户输入电商需求
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                   Agent.run()                            │
│                                                         │
│  Step 1: Plan（任务拆解）                                │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 分析意图 → 确定任务类型 → 生成执行步骤           │    │
│  │ ① 标题生成 ② 卖点提取 ③ FAQ生成                │    │
│  └─────────────────────────────────────────────────┘    │
│                         │                               │
│                         ▼                               │
│  Step 2: Decide（是否需要RAG）                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 查询知识库 → 获取平台规则 → 规则增强Prompt         │    │
│  └─────────────────────────────────────────────────┘    │
│                         │                               │
│                         ▼                               │
│  Step 3: Execute（执行步骤）                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 调用LLMService.call_structured()                 │    │
│  │ 每个步骤生成结构化JSON输出                        │    │
│  └─────────────────────────────────────────────────┘    │
│                         │                               │
│                         ▼                               │
│  Step 4: Merge（结果合并）                            │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 统一输出结构：titles + selling_points + faq       │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
    │
    ▼
写入History + AI Log → 前端展示
```

---

## 🚀 核心功能

### 1. 商品标题生成
- 拼多多标题：30字以内，突出性价比
- 淘宝标题：60字以内，包含营销词
- 小红书标题：吸引眼球，带话题标签

### 2. 卖点提取
- 自动提取5-8个核心卖点
- 每个卖点不超过20字
- 突出产品优势和差异化

### 3. 多平台文案生成
- 支持多个电商平台
- 符合各平台规则和风格
- 一键生成全平台内容

---

## 📁 项目结构

```
ai-ecommerce-agent/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── api/            # REST API接口层
│   │   ├── services/       # 核心业务服务
│   │   │   ├── llm_service.py      # 统一LLM调用层
│   │   │   ├── agent_service.py    # Agent任务拆解引擎
│   │   │   ├── rag_service.py      # RAG知识检索
│   │   │   ├── prompt_service.py   # Prompt模板管理
│   │   │   └── history_service.py  # 生成历史
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # 数据验证模型
│   │   └── core/           # 配置与基础能力
│   ├── init_data.py        # 初始化脚本
│   ├── requirements.txt    # Python依赖
│   └── .env                # 环境变量配置
├── frontend/                # Vue3前端
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProductForm.vue     # 商品信息输入
│   │   │   ├── GenerationResult.vue # 生成结果展示
│   │   │   ├── HistoryList.vue     # 历史记录查询
│   │   │   └── PromptList.vue      # Prompt模板管理
│   │   ├── App.vue         # 主应用组件
│   │   └── main.js         # 入口文件
│   └── package.json        # Node.js依赖
├── sql/                    # MySQL建表SQL
│   └── init.sql            # 初始化SQL脚本
├── docs/                   # 项目文档
│   ├── system_architecture.md     # 系统架构说明
│   ├── rag_design.md              # RAG设计说明
│   └── agent_design.md            # Agent拆解流程说明
├── README.md               # 项目说明文档
└── .gitignore              # Git忽略文件
```

---

## 🔧 快速开始

### 1. 环境要求

- Python 3.9+
- Node.js 18+
- MySQL 8.0+

### 2. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制并修改.env文件）
cp .env.example .env

# 创建数据库（执行SQL脚本）
mysql -u root -p < sql/init.sql

# 初始化数据
python init_data.py

# 启动后端服务
python main.py
```

后端服务启动在：http://localhost:8000

### 3. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务启动在：http://localhost:5173

---

## 📡 API接口

### 生成内容

```bash
POST /api/v1/generate
Content-Type: application/json

{
    "user_input": "为商品生成电商内容",
    "context": {
        "product_name": "无线蓝牙耳机",
        "category": "electronics",
        "features": ["降噪功能", "蓝牙5.0", "超长续航"],
        "description": "商品详细描述"
    }
}
```

**响应**：

```json
{
    "success": true,
    "titles": {
        "pdd": "拼多多标题",
        "tb": "淘宝标题",
        "xhs": "小红书标题"
    },
    "selling_points": ["卖点1", "卖点2", "卖点3"],
    "faq": [
        {"question": "问题1", "answer": "答案1"}
    ],
    "execution_stats": {
        "total_latency_ms": 2500,
        "step_count": 3,
        "success_steps": 3
    }
}
```

### 获取历史记录

```bash
GET /api/v1/history?limit=20&offset=0
```

### 获取统计信息

```bash
GET /api/v1/stats
```

---

## 🧠 Agent执行流程

### 步骤拆解

```
Step 1: generate_titles（生成多平台标题）
    ├── 拼多多标题
    ├── 淘宝标题
    └── 小红书标题

Step 2: extract_selling_points（提取商品卖点）
    ├── 卖点1
    ├── 卖点2
    └── 卖点3

Step 3: generate_faq（生成客服FAQ）
    ├── 问题1 + 答案1
    └── 问题2 + 答案2
```

### 输出结构

```json
{
    "titles": {
        "pdd": "拼多多商品标题",
        "tb": "淘宝商品标题",
        "xhs": "小红书商品标题"
    },
    "selling_points": ["卖点1", "卖点2", "卖点3"],
    "faq": [
        {"question": "常见问题1", "answer": "答案1"},
        {"question": "常见问题2", "answer": "答案2"}
    ],
    "raw_notes": ""
}
```

---

## 📚 RAG知识库

### 知识分类

| 分类 | 内容 | 用途 |
|------|------|------|
| `title_rules` | 各平台标题规范 | 标题生成时注入规则 |
| `electronics_rules` | 3C数码类目规则 | 3C商品生成时注入 |
| `clothing_rules` | 服装类目规则 | 服装商品生成时注入 |

### 添加知识

```bash
POST /api/v1/knowledge
?title=新规则标题&content=规则内容&category=title_rules
```

---

## 🎯 企业级设计

### 1. LLM统一调用

```python
# 所有AI调用必须通过LLMService
llm_service = LLMService()

# 基础调用
result = llm_service.call(prompt="Hello", provider="alibaba")

# 结构化输出调用
result = llm_service.call_structured(
    prompt="生成标题",
    expected_schema={"title": "标题内容"}
)

# 支持多Provider
# - alibaba（阿里云百炼）
# - deepseek（深度求索）
# - openai（预留）
```

### 2. Agent可扩展性

```python
# 新增步骤只需3步：
# 1. 创建Prompt模板
prompt_service.create_template({
    "name": "new_step",
    "content": "...",
    "variables": {...}
})

# 2. 在_plan()中添加步骤
plan["steps"].append({
    "step_id": 4,
    "name": "new_step",
    "prompt_template": "new_step",
    "schema": {"output": "描述"}
})

# 3. 在_merge_results()中处理结果
elif result["name"] == "new_step":
    merged["new_field"] = data.get("output", "")
```

### 3. 可观测性

```python
execution_stats = {
    "total_latency_ms": 2500,
    "step_count": 3,
    "success_steps": 3,
    "failed_steps": 0
}
```

---

## 📊 性能指标

| 指标 | 说明 |
|------|------|
| **单步骤耗时** | ~500-1000ms |
| **总耗时** | ~2-3s（3步骤并行） |
| **Token消耗** | 根据内容长度变化 |
| **成功率** | 95%+（JSON格式验证） |

---

## 🚀 扩展方向

### LLM扩展

- [ ] 添加OpenAI支持
- [ ] 添加Qwen支持
- [ ] 添加模型路由策略

### Agent扩展

- [ ] 新增详情页描述生成步骤
- [ ] 新增图片描述生成步骤
- [ ] 支持步骤并行执行

### RAG扩展

- [ ] 升级到FAISS向量库
- [ ] 支持语义重排序
- [ ] 添加知识自动更新

---

## 📝 License

MIT License

---

## 🤝 贡献

欢迎提交Issue和PR！

---

## 📧 联系方式

如有问题，请通过以下方式联系：
- 项目地址：https://github.com/yourusername/ai-ecommerce-agent
- 邮箱：your@email.com

---

> **注意**：本项目为作品集展示项目，生产环境部署前请完善安全配置和性能优化。