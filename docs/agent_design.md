# Agent拆解流程说明

## 1. 设计动机

### 1.1 为什么需要Agent？

在电商内容生成场景中，直接调用LLM存在以下问题：

| 问题             | 描述                           | 影响                           |
| ---------------- | ------------------------------ | ------------------------------ |
| **可控性差**     | LLM自主决定输出结构和内容      | 输出格式不稳定，难以预测       |
| **规则注入困难** | 所有规则必须在单个prompt中注入 | Prompt过长，LLM注意力分散      |
| **调试困难**     | 单次调用出问题难以定位         | 无法确定是哪个环节出错         |
| **扩展性差**     | 修改prompt影响全局             | 新增平台需要重新设计整个prompt |
| **可观测性差**   | 无法追踪中间过程               | 难以分析性能瓶颈和优化点       |

### 1.2 Agent方案的优势

```
传统方案（单次LLM调用）:
用户输入 → LLM → 输出（质量不可控）

Agent方案（多步骤拆解）:
用户输入 → Agent拆解 → 步骤1标题 → 步骤2卖点 → 步骤3FAQ → 合并输出

优势：
1. 可控性：每个步骤有明确的目标和输出格式
2. 规则注入：可在特定步骤注入针对性规则
3. 可调试：可定位到具体步骤
4. 扩展性：新增步骤不影响其他步骤
5. 可观测：每步骤有独立的执行统计
```

---

## 2. Agent架构

```
┌─────────────────────────────────────────────────────────────┐
│                     EcommerceAgent                          │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Planner    │───▶│   Executor   │───▶│   Merger     │  │
│  │  任务规划器   │    │  步骤执行器   │    │  结果合并器   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  TaskPlan    │    │ LLMService   │    │ OutputSchema │  │
│  │  执行计划    │    │  统一调用层   │    │  输出结构     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │  RAGService  │    │PromptService │                      │
│  │  知识检索     │    │  Prompt模板  │                      │
│  └──────────────┘    └──────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 核心流程

### 3.1 流程总览

```
用户输入："为商品'无线蓝牙耳机'生成电商内容"
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                    Agent.run()                          │
│                                                         │
│  Step 1: Plan（任务拆解）                                │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 分析用户意图 → 确定任务类型 → 生成执行步骤         │    │
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
│  │ Step 3.1: 生成多平台标题                         │    │
│  │ Step 3.2: 提取商品卖点                           │    │
│  │ Step 3.3: 生成客服FAQ                            │    │
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
输出：{
    "titles": { "pdd": "...", "tb": "...", "xhs": "..." },
    "selling_points": ["...", "...", "..."],
    "faq": [{ "question": "...", "answer": "..." }],
    "execution_stats": { "total_latency_ms": 2500 }
}
```

---

## 4. 三步拆解逻辑

### 4.1 Step 1: Plan（任务拆解）

```python
def _plan(self, user_input, context):
    """
    任务拆解逻辑：

    1. 分析用户输入和上下文
    2. 确定任务类型（content_generation）
    3. 确定商品类目
    4. 判断是否需要RAG增强
    5. 生成执行步骤列表
    """

    plan = {
        "task_type": "content_generation",
        "category": context.get("category", "general"),
        "requires_rag": True,  # 电商内容生成需要规则指导

        "steps": [
            {
                "step_id": 1,
                "name": "generate_titles",
                "description": "生成多平台商品标题",
                "prompt_template": "title_generation",
                "schema": {
                    "pdd": "拼多多标题，30字以内，包含关键词",
                    "tb": "淘宝标题，60字以内，包含营销词",
                    "xhs": "小红书标题，吸引眼球，带话题"
                }
            },
            {
                "step_id": 2,
                "name": "extract_selling_points",
                "description": "提取商品核心卖点",
                "prompt_template": "selling_points_extraction",
                "schema": {
                    "selling_points": "卖点列表，每个卖点不超过20字"
                }
            },
            {
                "step_id": 3,
                "name": "generate_faq",
                "description": "生成客服常见问题",
                "prompt_template": "faq_generation",
                "schema": {
                    "faq": "FAQ列表，包含问题和答案"
                }
            }
        ]
    }

    return plan
```

**设计原因**：

```
1. 任务拆解：将复杂任务拆分为独立子任务，每个子任务有明确目标
2. 步骤定义：每个步骤包含ID、名称、描述、模板和输出结构
3. RAG判断：根据任务类型和类目判断是否需要知识增强
4. 可扩展性：步骤列表可动态增减，不影响核心逻辑
```

### 4.2 Step 2: Decide（RAG决策）

```python
def _retrieve_rules(self, category):
    """
    规则检索逻辑：

    1. 根据类目获取标题规范
    2. 根据类目获取类目特定规则
    3. 拼接成规则上下文
    """

    rules = []

    # 获取标题规范（所有类目通用）
    title_rules = self.rag_service.get_rules_for_category("title_rules")
    if title_rules:
        rules.append(f"【标题规范】\n{title_rules}")

    # 获取类目特定规则
    category_rules = self.rag_service.get_rules_for_category(f"{category}_rules")
    if category_rules:
        rules.append(f"【类目规则】\n{category_rules}")

    return "\n\n".join(rules)
```

**设计原因**：

```
1. 规则分层：通用规则 + 类目特定规则，便于管理和维护
2. 动态注入：根据商品类目动态获取相关规则，避免规则冗余
3. 上下文构建：将规则拼接为统一格式，便于LLM理解
```

### 4.3 Step 3: Execute（步骤执行）

```python
def _execute_step(self, step, rules_context, context):
    """
    单步骤执行逻辑：

    1. 构建增强后的Prompt（包含规则上下文）
    2. 调用LLMService.call_structured()
    3. 验证JSON输出格式
    4. 返回步骤结果
    """

    # 构建Prompt
    prompt = f"""你是一个专业的电商运营助手。

商品信息：
- 商品名称：{context['product_name']}
- 商品特点：{', '.join(context['features'])}

{rules_context}

任务：{step['description']}

请严格按照以下JSON格式输出：
{{
{self._format_schema(step['schema'])}
}}"""

    # 调用LLM（强制结构化输出）
    result = llm_service.call_structured(
        prompt=prompt,
        expected_schema=step["schema"],
        temperature=0.7,
        max_tokens=1024
    )

    # 返回结果
    return {
        "step_id": step["step_id"],
        "name": step["name"],
        "success": result.success,
        "data": result.success ? json.loads(result.content) : {},
        "latency_ms": result.latency_ms,
        "tokens": {
            "input": result.input_tokens,
            "output": result.output_tokens
        }
    }
```

**设计原因**：

```
1. Prompt构建：统一格式，包含角色设定、商品信息、规则上下文和任务描述
2. 结构化输出：调用call_structured()强制JSON格式，确保输出可解析
3. 执行追踪：记录每步骤的执行时间和Token消耗，便于分析和优化
4. 错误处理：步骤失败时返回空数据，不影响其他步骤
```

### 4.4 Step 4: Merge（结果合并）

```python
def _merge_results(self, step_results):
    """
    结果合并逻辑：

    1. 遍历所有步骤结果
    2. 按步骤名称提取数据
    3. 统一到标准输出结构
    """

    merged = {
        "titles": { "pdd": "", "tb": "", "xhs": "" },
        "selling_points": [],
        "faq": [],
        "raw_notes": ""
    }

    for result in step_results:
        if not result["success"] or not result["data"]:
            continue

        data = result["data"]

        if result["name"] == "generate_titles":
            merged["titles"]["pdd"] = data.get("pdd", "")
            merged["titles"]["tb"] = data.get("tb", "")
            merged["titles"]["xhs"] = data.get("xhs", "")

        elif result["name"] == "extract_selling_points":
            merged["selling_points"] = data.get("selling_points", [])

        elif result["name"] == "generate_faq":
            merged["faq"] = data.get("faq", [])

    return merged
```

**设计原因**：

```
1. 统一结构：无论步骤如何变化，输出格式始终一致
2. 容错处理：跳过失败步骤，确保部分成功时仍能返回有效数据
3. 可扩展：新增步骤只需在合并逻辑中添加处理分支
```

---

## 5. 执行步骤详解

### 5.1 Step 3.1: 生成多平台标题

**输入**:

```
商品名称：无线蓝牙耳机
商品特点：降噪功能、蓝牙5.0、超长续航

【标题规范】
拼多多标题规范：30字以内，包含核心关键词...
淘宝标题规范：60字以内，包含营销词...
小红书标题规范：吸引眼球，带话题...

任务：生成多平台商品标题
```

**输出**:

```json
{
  "pdd": "无线蓝牙耳机降噪蓝牙5.0超长续航包邮",
  "tb": "2024新款无线蓝牙耳机主动降噪蓝牙5.0超长续航运动跑步专用",
  "xhs": "挖到宝了！这款蓝牙耳机降噪绝了🎧#好物推荐"
}
```

### 5.2 Step 3.2: 提取商品卖点

**输入**:

```
商品名称：无线蓝牙耳机
商品特点：降噪功能、蓝牙5.0、超长续航
商品描述：采用最新蓝牙5.0技术，支持主动降噪，续航长达30小时

任务：提取商品核心卖点
```

**输出**:

```json
{
  "selling_points": [
    "主动降噪技术",
    "蓝牙5.0稳定连接",
    "30小时超长续航",
    "舒适佩戴设计",
    "IPX5防水等级"
  ]
}
```

### 5.3 Step 3.3: 生成客服FAQ

**输入**:

```
商品名称：无线蓝牙耳机
商品特点：降噪功能、蓝牙5.0、超长续航

任务：生成客服常见问题及答案
```

**输出**:

```json
{
  "faq": [
    {
      "question": "这款耳机支持哪些设备？",
      "answer": "支持所有蓝牙5.0及以上版本的设备，包括手机、电脑、平板等。"
    },
    {
      "question": "充电一次能用多久？",
      "answer": "单次充电可使用8小时，搭配充电仓总续航可达30小时。"
    },
    {
      "question": "支持主动降噪吗？",
      "answer": "支持主动降噪功能，可有效隔绝环境噪音。"
    }
  ]
}
```

---

## 6. Agent扩展能力

### 6.1 新增步骤

```python
def _plan(self, user_input, context):
    plan = super()._plan(user_input, context)

    # 新增步骤：生成详情页描述
    plan["steps"].append({
        "step_id": 4,
        "name": "generate_description",
        "description": "生成商品详情页描述",
        "prompt_template": "description_generation",
        "schema": {
            "description": "商品详情描述，500字左右"
        }
    })

    return plan
```

### 6.2 步骤依赖

```python
# 支持步骤依赖，顺序执行
steps = [
    {
        "step_id": 1,
        "name": "extract_features",
        "depends_on": []  # 无依赖，可立即执行
    },
    {
        "step_id": 2,
        "name": "generate_title",
        "depends_on": [1]  # 依赖步骤1的结果
    }
]
```

### 6.3 并行执行

```python
# 无依赖的步骤可以并行执行
# Step 1, 2, 3 无依赖，可并行
# Step 4 依赖 Step 1，需等 Step 1 完成
```

---

## 7. 企业级设计特点

### 7.1 结构化输出保证

- 每个步骤强制要求JSON格式输出
- LLM返回后自动验证JSON格式
- 验证失败时标记步骤失败

### 7.2 执行追踪

- 记录每个步骤的执行时间
- 记录Token消耗
- 记录成功/失败状态
- 支持执行过程复盘

### 7.3 容错机制

- 单个步骤失败不影响其他步骤
- 失败步骤返回空数据
- 最终结果标记部分成功

### 7.4 可观测性

```python
execution_stats = {
    "total_latency_ms": 2500,
    "step_count": 3,
    "success_steps": 3,
    "failed_steps": 0
}
```

---

## 8. 对比：传统方案 vs Agent方案

| 维度         | 传统方案（单次LLM调用）            | Agent方案（多步骤拆解）          |
| ------------ | ---------------------------------- | -------------------------------- |
| **可控性**   | 低，LLM自主决定输出结构            | 高，每个步骤严格定义schema       |
| **规则注入** | 困难，需在单个prompt中注入所有规则 | 灵活，可在需要的步骤注入特定规则 |
| **可调试性** | 困难，单次调用出问题难以定位       | 简单，可定位到具体步骤           |
| **扩展性**   | 困难，修改prompt影响全局           | 简单，新增步骤不影响其他步骤     |
| **执行效率** | 快，单次调用                       | 稍慢，但可并行执行               |
| **输出质量** | 不稳定，依赖LLM理解能力            | 稳定，每步骤有明确目标           |
| **可观测性** | 差，无中间过程记录                 | 强，每步骤有独立统计             |

---

## 9. 面试亮点

### 9.1 为什么要做任务拆解？

```
1. 可控性：将复杂任务拆分为简单子任务，每个子任务有明确的目标和输出格式
2. 可维护性：修改某个步骤不影响其他步骤
3. 可扩展性：新增步骤只需在plan中添加，无需修改核心逻辑
4. 可观测性：每个步骤都有独立的执行统计，便于问题定位
5. 规则增强：可在特定步骤注入针对性规则
```

### 9.2 如何处理步骤失败？

```
1. 单个步骤失败不影响整体流程
2. 失败步骤返回空数据
3. 最终结果标记为"部分成功"
4. 记录失败原因到日志
5. 可配置重试策略
```

### 9.3 如何扩展新功能？

```python
# 只需3步：
# 1. 创建Prompt模板
prompt_service.create_template({
    "name": "new_step_template",
    "content": "...",
    "variables": {...}
})

# 2. 在_plan()中添加步骤
plan["steps"].append({
    "step_id": 4,
    "name": "new_step",
    "prompt_template": "new_step_template",
    "schema": {"output_field": "描述"}
})

# 3. 在_merge_results()中处理新步骤结果
elif result["name"] == "new_step":
    merged["new_field"] = data.get("output_field", "")
```

### 9.4 如果要支持步骤并行执行，如何设计？

```
1. 步骤定义中添加depends_on字段，标识依赖关系
2. 执行器根据依赖关系构建DAG（有向无环图）
3. 使用线程池或异步任务执行无依赖的步骤
4. 依赖步骤等待前置步骤完成后再执行
5. 结果合并时按步骤ID顺序合并，确保数据一致性
```

---

## 10. 扩展方向

### 10.1 步骤优化

- [ ] 支持步骤并行执行
- [ ] 添加步骤依赖关系管理
- [ ] 实现步骤级重试策略

### 10.2 Agent能力增强

- [ ] 支持动态任务规划（基于LLM生成步骤）
- [ ] 添加工具调用能力（搜索、计算等）
- [ ] 实现多轮对话交互

### 10.3 性能优化

- [ ] 添加步骤缓存（相同输入复用结果）
- [ ] 支持流式输出（实时返回生成结果）
- [ ] 实现异步任务队列
