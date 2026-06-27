# Prompt设计说明

## 1. Prompt设计概述

Prompt工程是AI应用开发中的核心环节。在本系统中，Prompt设计直接决定了LLM生成内容的质量和格式。通过精心设计的Prompt模板系统，我们实现了：

- **结构化输出保证**：强制LLM返回符合预期的JSON格式
- **变量替换机制**：支持动态注入商品信息和规则上下文
- **模板复用**：同一模板可用于不同商品的内容生成

## 2. 为什么需要Prompt模板系统

### 2.1 问题背景

在电商内容生成场景中，直接硬编码Prompt存在以下问题：

| 问题 | 描述 | 影响 |
|------|------|------|
| **维护困难** | Prompt分散在代码各处 | 修改规则需改动代码 |
| **一致性差** | 不同开发人员编写风格不一 | 生成质量波动大 |
| **扩展性差** | 新增平台需要修改代码 | 迭代周期长 |
| **不可追踪** | Prompt变更没有版本记录 | 难以回滚和审计 |

### 2.2 解决方案

将Prompt提取为独立的模板系统：

```
代码层（不变）
    ↓
Prompt模板（可配置）
    ↓
变量注入（动态替换）
    ↓
LLM生成（结构化输出）
```

## 3. Prompt模板结构

### 3.1 模板组成

每个Prompt模板包含以下组成部分：

| 组成部分 | 说明 | 示例 |
|----------|------|------|
| **name** | 模板唯一标识 | `title_generation` |
| **description** | 模板描述 | 生成多平台商品标题 |
| **content** | 模板内容（包含变量占位符） | 见下方示例 |
| **variables** | 变量定义 | `product_name`, `features`, `rules` |
| **schema** | 期望的输出结构 | JSON格式定义 |

### 3.2 模板示例：标题生成

```python
{
    "name": "title_generation",
    "description": "生成多平台商品标题",
    "content": """你是一个专业的电商运营助手。

商品信息：
- 商品名称：{{ product_name }}
- 商品特点：{{ features }}

{{ rules_context }}

任务：为以上商品生成适合以下平台的标题：
1. 拼多多标题：30字以内，突出性价比和促销信息
2. 淘宝标题：60字以内，包含营销词和长尾关键词
3. 小红书标题：吸引眼球，带话题标签，符合种草风格

请严格按照以下JSON格式输出，不要包含任何其他文字：
{
    "pdd": "拼多多标题内容",
    "tb": "淘宝标题内容",
    "xhs": "小红书标题内容"
}""",
    "variables": ["product_name", "features", "rules_context"],
    "schema": {
        "pdd": "拼多多标题，30字以内，包含关键词",
        "tb": "淘宝标题，60字以内，包含营销词",
        "xhs": "小红书标题，吸引眼球，带话题"
    }
}
```

### 3.3 模板示例：卖点提取

```python
{
    "name": "selling_points_extraction",
    "description": "提取商品核心卖点",
    "content": """你是一个专业的电商运营助手。

商品信息：
- 商品名称：{{ product_name }}
- 商品特点：{{ features }}
- 商品描述：{{ description }}

任务：从以上商品信息中提取5-8个核心卖点，每个卖点不超过20字。

请严格按照以下JSON格式输出：
{
    "selling_points": ["卖点1", "卖点2", "卖点3", "卖点4", "卖点5"]
}""",
    "variables": ["product_name", "features", "description"],
    "schema": {
        "selling_points": "卖点列表，每个卖点不超过20字"
    }
}
```

### 3.4 模板示例：FAQ生成

```python
{
    "name": "faq_generation",
    "description": "生成客服常见问题",
    "content": """你是一个专业的电商客服培训师。

商品信息：
- 商品名称：{{ product_name }}
- 商品特点：{{ features }}
- 商品描述：{{ description }}

任务：为以上商品生成5个常见的客服问题及答案，覆盖产品使用、售后、物流等场景。

请严格按照以下JSON格式输出：
{
    "faq": [
        {"question": "问题1", "answer": "答案1"},
        {"question": "问题2", "answer": "答案2"},
        {"question": "问题3", "answer": "答案3"},
        {"question": "问题4", "answer": "答案4"},
        {"question": "问题5", "answer": "答案5"}
    ]
}""",
    "variables": ["product_name", "features", "description"],
    "schema": {
        "faq": "FAQ列表，包含问题和答案"
    }
}
```

## 4. 变量替换机制

### 4.1 替换流程

```
模板内容（包含{{变量}}）
    ↓
变量字典（{变量名: 变量值}）
    ↓
字符串替换（jinja2模板引擎）
    ↓
最终Prompt（可直接调用LLM）
```

### 4.2 实现代码

```python
def render_prompt(self, template_name: str, variables: Dict[str, str]) -> str:
    """
    渲染Prompt模板
    
    参数：
        template_name: 模板名称
        variables: 变量字典
    
    返回：
        渲染后的完整Prompt
    """
    
    template = self.get_template(template_name)
    if not template:
        raise ValueError(f"Template {template_name} not found")
    
    # 使用jinja2进行变量替换
    from jinja2 import Template
    jinja_template = Template(template["content"])
    
    # 确保所有必需变量都已提供
    for var_name in template["variables"]:
        if var_name not in variables:
            variables[var_name] = ""
    
    return jinja_template.render(**variables)
```

### 4.3 调用示例

```python
# 准备变量
variables = {
    "product_name": "无线蓝牙耳机",
    "features": "降噪功能、蓝牙5.0、超长续航",
    "description": "高品质无线蓝牙耳机，支持主动降噪",
    "rules_context": "【标题规范】拼多多标题规范：30字以内..."
}

# 渲染Prompt
prompt = prompt_service.render_prompt("title_generation", variables)

# 调用LLM
result = llm_service.call_structured(prompt, expected_schema)
```

## 5. 结构化输出控制

### 5.1 为什么需要结构化输出

在企业级AI应用中，结构化输出至关重要：

| 原因 | 说明 |
|------|------|
| **数据可靠性** | JSON格式可直接解析，避免字符串处理错误 |
| **前后端对接** | 前端可以直接使用JSON数据渲染UI |
| **错误处理** | 可验证输出格式，及时发现问题 |
| **可维护性** | 输出结构清晰，便于扩展和修改 |

### 5.2 输出格式强制

通过在Prompt中明确指定JSON格式要求：

```python
# 在Prompt末尾添加格式要求
format_instruction = """

请严格按照以下JSON格式输出，不要包含任何其他文字、markdown格式或解释：
{{
{schema_str}
}}"""
```

### 5.3 输出验证机制

```python
def validate_json(self, content: str) -> Tuple[bool, Dict]:
    """
    验证LLM返回内容是否为有效JSON
    
    参数：
        content: LLM返回的原始内容
    
    返回：
        (是否有效, 解析后的数据)
    """
    
    try:
        # 清理可能存在的markdown代码块标记
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        data = json.loads(content)
        return True, data
    
    except json.JSONDecodeError as e:
        return False, {"error": str(e)}
```

### 5.4 失败重试策略

```python
def call_structured_with_retry(self, prompt, expected_schema, max_retries=3):
    """
    带重试的结构化输出调用
    
    参数：
        prompt: 提示词
        expected_schema: 期望的输出结构
        max_retries: 最大重试次数
    
    返回：
        LLMResponse
    """
    
    for attempt in range(max_retries):
        result = self.call_structured(prompt, expected_schema)
        
        if result.success:
            is_valid, data = self.validate_json(result.content)
            if is_valid:
                return result
        
        # 添加重试延迟
        time.sleep(1)
    
    return LLMResponse(
        success=False,
        error=f"Failed to generate valid JSON after {max_retries} attempts"
    )
```

## 6. Prompt优化策略

### 6.1 角色设定

在Prompt开头明确设定角色，帮助LLM理解任务背景：

```
你是一个专业的电商运营助手，熟悉各平台规则和内容创作技巧。
```

### 6.2 任务分解

将复杂任务分解为明确的子任务：

```
任务：
1. 分析商品特点
2. 根据平台规则生成标题
3. 确保符合字数限制和关键词要求
```

### 6.3 规则注入

通过RAG系统动态注入平台规则：

```
{{ rules_context }}

以上规则必须严格遵守！
```

### 6.4 示例引导

对于复杂任务，可以提供示例：

```
示例输出格式：
{
    "pdd": "【限时特惠】无线蓝牙耳机 降噪 超长续航",
    "tb": "2024新款无线蓝牙耳机主动降噪蓝牙5.0超长续航",
    "xhs": "挖到宝了！这副蓝牙耳机也太好用了吧 #蓝牙耳机"
}
```

### 6.5 约束条件

明确输出约束：

```
要求：
- 拼多多标题不超过30字
- 淘宝标题不超过60字
- 每个卖点不超过20字
- 必须包含核心关键词
```

## 7. Prompt版本管理

### 7.1 版本控制需求

| 场景 | 说明 |
|------|------|
| **A/B测试** | 测试不同Prompt版本的效果 |
| **回滚** | 新版本效果不佳时回滚到旧版本 |
| **审计** | 追踪Prompt变更历史 |
| **协作** | 多人协作开发Prompt |

### 7.2 版本管理实现

```sql
CREATE TABLE prompt_templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    version INT NOT NULL DEFAULT 1,
    content TEXT NOT NULL,
    description VARCHAR(500),
    variables JSON,
    schema JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (name, version)
);
```

### 7.3 版本切换

```python
def get_template(self, name: str, version: int = None) -> Dict:
    """
    获取Prompt模板
    
    参数：
        name: 模板名称
        version: 版本号（默认获取最新版本）
    
    返回：
        模板数据
    """
    
    if version:
        return self.db.query(PromptTemplate).filter(
            PromptTemplate.name == name,
            PromptTemplate.version == version
        ).first()
    
    return self.db.query(PromptTemplate).filter(
        PromptTemplate.name == name
    ).order_by(PromptTemplate.version.desc()).first()
```

## 8. 面试亮点

### 8.1 如何保证结构化输出？

```
1. Prompt设计：在Prompt末尾明确指定JSON格式要求
2. 格式验证：LLM返回后自动验证JSON格式
3. 失败重试：验证失败时自动重试（最多3次）
4. 容错机制：所有步骤失败时返回默认空数据
```

### 8.2 为什么要用模板系统？

```
1. 可维护性：修改Prompt无需改动代码
2. 一致性：统一管理所有Prompt，风格一致
3. 扩展性：新增平台只需添加模板
4. 可追踪：支持版本控制，便于回滚和审计
```

### 8.3 Prompt如何优化？

```
1. 角色设定：明确LLM的角色和任务背景
2. 任务分解：将复杂任务拆分为明确的子任务
3. 规则注入：动态注入平台规则和约束条件
4. 示例引导：提供示例输出帮助LLM理解格式
5. 约束明确：明确字数、格式、关键词等要求
```

### 8.4 如何处理Prompt泄露？

```
1. 不在前端暴露Prompt模板
2. API层不返回完整Prompt内容
3. 使用环境变量管理敏感信息
4. 日志脱敏：记录时不包含完整Prompt
```

## 9. 扩展方向

### 9.1 Prompt优化工具
- [ ] 集成Prompt调试工具
- [ ] 添加Prompt性能分析
- [ ] 支持A/B测试框架

### 9.2 智能Prompt生成
- [ ] 基于历史数据自动优化Prompt
- [ ] 根据商品类目自动选择模板
- [ ] 动态调整Prompt参数（temperature等）

### 9.3 多语言支持
- [ ] 支持多语言Prompt模板
- [ ] 自动翻译商品信息
- [ ] 生成多语言内容
