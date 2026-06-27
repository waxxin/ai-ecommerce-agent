# AI E-commerce Agent 🤖

> 基于 LLM 的企业级电商内容生成系统 | Enterprise AI Content Generation Platform for E-commerce

一个完整的 AI 电商运营 Agent 系统，支持多平台商品标题生成、卖点提取、FAQ 生成，引入 RAG 知识检索增强生成质量，前后端完整闭环。

---

## ✨ 项目亮点

| 亮点                 | 描述                                                                   |
| -------------------- | ---------------------------------------------------------------------- |
| **Agent 多步骤系统** | 将 LLM 单次调用升级为任务拆解、规则检索、步骤执行、结果合并的完整流程  |
| **RAG 规则增强**     | 知识库注入平台规则，确保生成内容符合各平台规范，提升生成稳定性         |
| **结构化输出保证**   | 强制 JSON 格式输出，避免 LLM 幻觉导致的解析错误，确保前后端数据一致性  |
| **可观测性设计**     | 记录每步骤执行时间、Token 消耗，支持执行过程复盘和性能优化             |
| **工程化架构**       | Vue3 前端 + FastAPI 后端 + MySQL 数据库 + LLM 服务端，完整的企业级架构 |

---

## 🛠 技术栈

| 层级            | 技术                  | 版本    |
| --------------- | --------------------- | ------- |
| **前端框架**    | Vue3                  | 3.5.x   |
| **UI 组件库**   | Element Plus          | 2.9.x   |
| **HTTP 客户端** | Axios                 | 1.7.x   |
| **构建工具**    | Vite                  | 6.5.x   |
| **后端框架**    | FastAPI               | 0.115.x |
| **ORM**         | SQLAlchemy            | 2.0.x   |
| **数据库**      | MySQL                 | 8.0+    |
| **LLM 服务**    | 阿里云百炼 / DeepSeek | -       |
| **向量检索**    | Sentence Transformers | 3.0.x   |

---

## 🏗 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户输入层                                │
│              Vue3 Frontend (ProductForm)                        │
│           商品名称 / 类目 / 特点 / 描述                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ POST /api/v1/generate
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API 接口层                                │
│                    FastAPI Router                               │
│              请求验证 → 业务分发 → 响应格式化                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Agent 引擎层                              │
│                   EcommerceAgent.run()                          │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Plan    │ → │  Decide  │ → │ Execute  │ → │  Merge   │  │
│  │ 任务拆解 │    │ RAG检索  │    │ 步骤执行 │    │ 结果合并 │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│         │              │              │              │         │
│         ▼              ▼              ▼              ▼         │
│    ①标题生成     查询知识库    LLMService      统一JSON        │
│    ②卖点提取     规则增强     .call_structured()               │
│    ③FAQ生成      Prompt                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据持久层                                │
│              GenerationHistory + AILog + PromptTemplate         │
│                    MySQL Database                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        LLM 服务层                                │
│              LLMService (Alibaba / DeepSeek / OpenAI)           │
│                   统一接口 · 多模型扩展                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 核心功能

### 1. 商品标题生成

- **拼多多标题**：30字以内，突出性价比和促销信息
- **淘宝标题**：60字以内，包含营销词和长尾关键词
- **小红书标题**：吸引眼球，带话题标签，符合种草风格

### 2. 卖点提取

- 自动提取 5-8 个核心卖点
- 每个卖点不超过 20 字
- 突出产品优势和差异化竞争点

### 3. 多平台文案生成

- 支持多个电商平台的文案风格
- 符合各平台规则和内容规范
- 一键生成全平台适用的内容

### 4. 客服 FAQ 生成

- 自动生成常见问题和解答
- 覆盖产品使用、售后、物流等场景
- 提升客服效率和用户体验

---

## 📁 项目结构

```
ai-ecommerce-agent/
├── backend/                          # FastAPI 后端
│   ├── app/
│   │   ├── api/__init__.py           # REST API 路由
│   │   ├── services/                 # 核心业务服务
│   │   │   ├── llm_service.py        # 统一 LLM 调用层
│   │   │   ├── agent_service.py      # Agent 任务拆解引擎
│   │   │   ├── rag_service.py        # RAG 知识检索服务
│   │   │   ├── prompt_service.py     # Prompt 模板管理
│   │   │   └── history_service.py    # 生成历史管理
│   │   ├── models/__init__.py        # SQLAlchemy 模型
│   │   ├── schemas/__init__.py       # Pydantic 验证模型
│   │   └── core/                     # 配置与基础能力
│   │       ├── config.py             # 环境配置管理
│   │       └── database.py           # 数据库连接管理
│   ├── main.py                       # FastAPI 应用入口
│   ├── requirements.txt              # Python 依赖清单
│   └── init_data.py                  # 初始化脚本
├── frontend/                         # Vue3 前端
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProductForm.vue       # 商品信息输入表单
│   │   │   ├── GenerationResult.vue  # 生成结果展示
│   │   │   ├── HistoryList.vue       # 历史记录查询
│   │   │   └── PromptList.vue        # Prompt 模板管理
│   │   ├── App.vue                   # 主应用组件
│   │   └── main.js                   # 入口文件
│   ├── index.html                    # HTML 入口
│   ├── package.json                  # Node.js 依赖
│   └── vite.config.js                # Vite 配置
├── sql/                              # MySQL 建表脚本
│   └── init.sql                      # 数据库初始化脚本
├── docs/                             # 项目文档
│   ├── system_architecture.md        # 系统架构说明
│   ├── agent_design.md               # Agent 拆解流程说明
│   └── rag_design.md                 # RAG 设计说明
├── .gitignore                        # Git 忽略配置
└── README.md                         # 项目说明文档
```

---

## 🔧 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- MySQL 8.0+

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 创建数据库
mysql -u root -p
CREATE DATABASE ai_ecommerce CHARACTER SET utf8mb4;

# 初始化数据
python init_data.py

# 启动后端服务
python main.py
```

后端服务启动在：http://localhost:8000

### 前端启动

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

## 📡 API 接口

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
        "description": "高品质无线蓝牙耳机，支持主动降噪"
    }
}
```

**响应**：

```json
{
  "success": true,
  "titles": {
    "pdd": "【限时特惠】无线蓝牙耳机 降噪 超长续航 蓝牙5.0",
    "tb": "2024新款无线蓝牙耳机主动降噪蓝牙5.0超长续航运动耳机",
    "xhs": "挖到宝了！这副蓝牙耳机也太好用了吧 #蓝牙耳机推荐"
  },
  "selling_points": [
    "主动降噪，沉浸式体验",
    "蓝牙5.0，连接稳定",
    "超长续航，全天无忧",
    "轻巧便携，舒适佩戴"
  ],
  "faq": [
    { "question": "支持哪些设备？", "answer": "支持所有蓝牙5.0及以上设备" },
    { "question": "续航多久？", "answer": "单次续航8小时，充电盒总续航32小时" }
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

---

## 🧠 Agent 执行流程

### 步骤拆解

```
Step 1: generate_titles（生成多平台标题）
    ├── 拼多多标题（30字以内）
    ├── 淘宝标题（60字以内）
    └── 小红书标题（带话题）

Step 2: extract_selling_points（提取商品卖点）
    ├── 卖点1（20字以内）
    ├── 卖点2（20字以内）
    └── 卖点3（20字以内）

Step 3: generate_faq（生成客服FAQ）
    ├── 问题1 + 答案1
    └── 问题2 + 答案2
```

### 输出结构

所有 AI 返回统一 JSON 格式：

```json
{
  "titles": {
    "pdd": "拼多多商品标题",
    "tb": "淘宝商品标题",
    "xhs": "小红书商品标题"
  },
  "selling_points": ["卖点1", "卖点2", "卖点3"],
  "faq": [
    { "question": "常见问题1", "answer": "答案1" },
    { "question": "常见问题2", "answer": "答案2" }
  ],
  "raw_notes": ""
}
```

---

## 📚 RAG 知识库

### 知识分类

| 分类                | 内容                           | 用途               |
| ------------------- | ------------------------------ | ------------------ |
| `title_rules`       | 各平台标题字数限制、关键词要求 | 标题生成时注入规则 |
| `electronics_rules` | 3C数码类目规范、禁用词         | 3C商品生成时注入   |
| `clothing_rules`    | 服装类目规则、材质描述规范     | 服装商品生成时注入 |

### 检索流程

```
用户输入 → Embedding → 向量检索(topK=3) → 规则拼接 → Prompt构造 → LLM生成
```

---

## 🎯 企业级设计

### 1. LLM 统一调用

```python
# 所有 AI 调用必须通过 LLMService
llm_service = LLMService()

# 基础调用
result = llm_service.call(prompt="Hello", provider="alibaba")

# 结构化输出调用（强制 JSON 格式）
result = llm_service.call_structured(
    prompt="生成标题",
    expected_schema={"title": "标题内容"}
)

# 支持多 Provider 扩展
# - alibaba（阿里云百炼）
# - deepseek（深度求索）
# - openai（预留）
```

### 2. Agent 可扩展性

新增步骤只需 3 步：

```python
# 1. 创建 Prompt 模板
prompt_service.create_template({
    "name": "new_step",
    "content": "...",
    "variables": {...}
})

# 2. 在 _plan() 中添加步骤
plan["steps"].append({
    "step_id": 4,
    "name": "new_step",
    "prompt_template": "new_step",
    "schema": {"output": "描述"}
})

# 3. 在 _merge_results() 中处理结果
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

| 指标           | 说明                   |
| -------------- | ---------------------- |
| **单步骤耗时** | ~500-1000ms            |
| **总耗时**     | ~2-3s（3步骤顺序执行） |
| **Token 消耗** | 根据内容长度变化       |
| **成功率**     | 95%+（JSON 格式验证）  |

---

## 🚀 扩展方向

### LLM 扩展

- [ ] 添加 OpenAI 支持
- [ ] 添加 Qwen 支持
- [ ] 添加模型路由策略

### Agent 扩展

- [ ] 新增详情页描述生成步骤
- [ ] 新增图片描述生成步骤
- [ ] 支持步骤并行执行

### RAG 扩展

- [ ] 升级到 FAISS 向量库
- [ ] 支持语义重排序
- [ ] 添加知识自动更新

---

## 📝 License

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

---

## 📧 联系方式

- **项目地址**：https://github.com/waxxin/ai-ecommerce-agent
- **邮箱**：3235977737@email.com

---

> **注意**：本项目为作品集展示项目，生产环境部署前请完善安全配置和性能优化。
