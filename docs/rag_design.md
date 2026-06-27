# RAG设计说明

## 1. 设计动机

### 1.1 为什么需要RAG？

在电商内容生成场景中，直接使用LLM存在以下问题：

| 问题               | 描述                                        | 影响               |
| ------------------ | ------------------------------------------- | ------------------ |
| **知识有限**       | LLM训练数据截止到特定时间，无法获取最新规则 | 生成的内容可能过时 |
| **规则记忆不准确** | LLM可能记错或混淆平台规则                   | 内容不符合平台规范 |
| **缺乏领域知识**   | LLM不了解电商类目特定规则                   | 内容不够专业       |
| **难以更新**       | 更新LLM需要重新训练                         | 规则变更响应慢     |

### 1.2 RAG方案的优势

```
传统方案（纯LLM）:
用户输入 → LLM → 输出（知识有限，可能不符合规则）

RAG方案（检索增强）:
用户输入 → 检索知识库 → 规则增强Prompt → LLM → 输出（符合规则）

优势：
1. 规则准确：直接从知识库获取最新规则
2. 领域专业：包含类目特定知识
3. 易于更新：规则变更只需更新知识库
4. 可控性强：生成内容符合预期规范
```

### 1.3 电商场景的特殊需求

```
1. 平台规则复杂：拼多多/淘宝/小红书各有不同规则
2. 规则变化频繁：平台不定期更新规则
3. 类目规则多样：3C/服装/美妆等类目规则不同
4. 合规要求高：违规内容可能导致商品下架
```

---

## 2. RAG架构

```
┌─────────────────────────────────────────────────────────────┐
│                     RAG Pipeline                            │
│                                                             │
│  用户查询                                                     │
│      │                                                      │
│      ▼                                                      │
│  ┌──────────────┐                                           │
│  │  Embedding   │  使用Sentence Transformers生成向量         │
│  │  (向量化)    │                                           │
│  └──────┬───────┘                                           │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐                                           │
│  │ Vector       │  余弦相似度检索Top-K相似文档               │
│  │ Search       │                                           │
│  └──────┬───────┘                                           │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐                                           │
│  │ Context      │  将检索到的知识拼接到Prompt中              │
│  │ Augmentation │                                           │
│  └──────┬───────┘                                           │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐                                           │
│  │ LLM Generate │  LLM基于增强后的Prompt生成内容             │
│  └──────────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 知识库构建

### 3.1 知识分类

| 分类                | 内容                                   | 用途               |
| ------------------- | -------------------------------------- | ------------------ |
| `title_rules`       | 各平台标题规范（字数限制、关键词要求） | 标题生成时注入规则 |
| `electronics_rules` | 3C数码类目规则（禁用词、专业术语）     | 3C商品生成时注入   |
| `clothing_rules`    | 服装类目规则（材质描述、尺码规范）     | 服装商品生成时注入 |
| `beauty_rules`      | 美妆类目规则（成分标注、功效宣称）     | 美妆商品生成时注入 |
| `food_rules`        | 食品类目规则（生产日期、保质期）       | 食品商品生成时注入 |
| `home_rules`        | 家居类目规则（尺寸描述、材质要求）     | 家居商品生成时注入 |

### 3.2 知识库数据表

```sql
CREATE TABLE knowledge_base (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,    -- 知识标题
    content TEXT NOT NULL,          -- 知识内容
    category VARCHAR(100),          -- 知识分类
    source VARCHAR(200),            -- 来源（如平台规则文档）
    embedding JSON,                 -- 向量化结果（384维向量）
    is_active BOOLEAN DEFAULT TRUE, -- 是否启用
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_is_active (is_active)
);
```

### 3.3 知识库初始化数据

```python
# 示例：标题规范知识
title_rules = {
    "title": "电商平台标题规范",
    "content": """【拼多多标题规范】
1. 标题长度：不超过30字
2. 必须包含核心关键词
3. 可使用促销词：包邮、限时、特惠、爆款等
4. 禁止使用绝对化用语：最、第一、顶级等
5. 禁止使用违规词：国家级、老字号等

【淘宝标题规范】
1. 标题长度：不超过60字
2. 包含营销词和长尾关键词
3. 关键词布局：前10字放置核心词
4. 可使用空格分隔关键词
5. 禁止重复关键词超过3次

【小红书标题规范】
1. 语气：亲切、种草风格
2. 使用表情符号增加吸引力
3. 包含话题标签（#话题名）
4. 长度：20-40字为宜
5. 引发好奇心：使用疑问、感叹句式""",
    "category": "title_rules",
    "source": "平台规则文档"
}

# 示例：3C数码类目规则
electronics_rules = {
    "title": "3C数码类目规则",
    "content": """【3C数码类目规则】
1. 必须标注品牌名称
2. 标注核心参数：型号、规格、功能
3. 禁止虚假宣传：如实描述功能
4. 标注认证信息：3C认证、入网许可
5. 禁止使用医疗术语：如"治疗"、"疗效"等
6. 电池相关：标注容量、充电方式
7. 接口类型：USB-C、Lightning等""",
    "category": "electronics_rules",
    "source": "平台规则文档"
}
```

---

## 4. 核心实现

### 4.1 Embedding生成

```python
def _compute_embedding(self, text: str) -> List[float]:
    """
    使用Sentence Transformers生成文本向量

    参数：
        text: 待向量化的文本

    返回：
        384维向量（List[float]）
    """

    if not self.embedding_model:
        return [0.0] * 384  # 返回零向量

    return self.embedding_model.encode(text).tolist()
```

**设计原因**：

```
1. 轻量模型：Sentence Transformers是轻量级模型，适合本地部署
2. 语义相似度：生成的向量能很好地表示文本语义
3. 预训练模型：使用预训练模型，无需从头训练
4. 可扩展性：支持切换到其他embedding模型
```

### 4.2 向量检索

```python
def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    检索相关知识

    流程：
    1. 将查询文本向量化
    2. 计算与知识库中所有文档的余弦相似度
    3. 返回Top-K最相似的文档

    参数：
        query: 查询文本
        top_k: 返回数量（默认3条）

    返回：
        相似文档列表（包含相似度分数）
    """

    query_embedding = self._compute_embedding(query)

    results = []
    for item_id, item_data in self.vector_store.items():
        similarity = self._cosine_similarity(query_embedding, item_data["embedding"])
        if similarity > 0.3:  # 相似度阈值过滤
            results.append({
                "id": item_id,
                "title": item_data["title"],
                "content": item_data["content"],
                "similarity": round(similarity, 4)
            })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]
```

**设计原因**：

```
1. 余弦相似度：衡量向量之间的夹角，适合语义相似度计算
2. 阈值过滤：过滤相似度低于0.3的文档，避免不相关知识干扰
3. Top-K限制：只返回最相关的3条，避免Prompt过长
4. 排序机制：按相似度降序排列，确保最相关的知识优先
```

### 4.3 规则增强

```python
def get_rules_for_category(self, category: str) -> str:
    """
    获取指定类目的规则

    参数：
        category: 类目名称

    返回：
        规则上下文字符串
    """

    # 获取标题规范（所有类目通用）
    title_rules = self.get_rules("title_rules")

    # 获取类目规则
    category_rules = self.get_rules(f"{category}_rules")

    # 拼接成上下文
    return f"【标题规范】\n{title_rules}\n\n【类目规则】\n{category_rules}"
```

**设计原因**：

```
1. 分层规则：通用规则 + 类目特定规则，避免规则冗余
2. 动态注入：根据商品类目动态获取相关规则
3. 格式统一：使用【】标记规则类型，便于LLM理解
4. 可扩展性：新增类目只需添加对应规则，无需修改代码
```

---

## 5. 在Agent中的应用

```python
def run(self, user_input, context):
    """
    Agent主流程

    1. 规划任务
    2. 判断是否需要RAG
    3. 检索规则并增强Prompt
    4. 执行步骤
    5. 合并结果
    """

    # Step 1: 规划任务
    plan = self._plan(user_input, context)

    # Step 2: 判断是否需要RAG
    rules_context = ""
    if plan["requires_rag"]:
        rules_context = self._retrieve_rules(plan["category"])

    # Step 3: 执行步骤（规则已注入Prompt）
    step_results = []
    for step in plan["steps"]:
        # 构建增强后的Prompt
        prompt = self._build_prompt(step, rules_context, context)

        # 调用LLM（强制结构化输出）
        result = llm_service.call_structured(prompt, step["schema"])

        step_results.append(result)

    # Step 4: 合并结果
    final_result = self._merge_results(step_results)

    return final_result
```

---

## 6. RAG效果

### 6.1 无RAG时的问题

```
示例：生成无线蓝牙耳机标题

无RAG输出（可能不符合规则）：
- 拼多多："无线蓝牙耳机降噪功能超长续航蓝牙5.0技术顶级音质"（超过30字，使用"顶级"违规词）
- 淘宝："蓝牙耳机"（太短，缺少关键词）
- 小红书："无线蓝牙耳机介绍"（过于平淡，不符合种草风格）
```

### 6.2 RAG增强后的效果

```
示例：生成无线蓝牙耳机标题

RAG增强输出（符合规则）：
- 拼多多："无线蓝牙耳机降噪蓝牙5.0超长续航包邮"（30字以内，包含促销词）
- 淘宝："2024新款无线蓝牙耳机主动降噪蓝牙5.0超长续航运动跑步专用"（60字以内，包含营销词和长尾词）
- 小红书："挖到宝了！这款蓝牙耳机降噪绝了🎧#好物推荐"（种草风格，带话题标签）
```

### 6.3 效果对比

| 维度         | 无RAG                | RAG增强                |
| ------------ | -------------------- | ---------------------- |
| **合规性**   | 低，可能违规         | 高，符合平台规则       |
| **质量**     | 一般，缺乏专业描述   | 高，包含类目专业知识   |
| **一致性**   | 不稳定，风格不一     | 稳定，同类商品描述统一 |
| **可维护性** | 规则变更需要修改代码 | 规则变更只需更新知识库 |

---

## 7. 优化方向

### 7.1 向量库升级

| 阶段 | 方案                               | 适用场景                 | 升级原因             |
| ---- | ---------------------------------- | ------------------------ | -------------------- |
| 当前 | Sentence Transformers + 内存向量库 | 小型知识库(<1000条)      | 快速开发，零依赖     |
| 中级 | FAISS本地向量库                    | 中型知识库(1000-10000条) | 性能提升，支持索引   |
| 高级 | Milvus/Pinecone                    | 大型知识库(>10000条)     | 分布式部署，水平扩展 |

### 7.2 检索策略优化

1. **语义重排序**：对检索结果进行语义排序，提升相关性
2. **多跳检索**：支持复杂问题的多步推理和检索
3. **混合检索**：结合关键词检索和向量检索，提升准确性
4. **查询扩展**：对用户查询进行扩展，覆盖更多相关知识

### 7.3 知识管理

1. **自动更新**：定期从外部源（如平台规则文档）更新知识库
2. **版本控制**：追踪知识变更历史，支持回滚
3. **过期淘汰**：自动清理过期知识，保持知识库新鲜
4. **知识审核**：新增知识需经过审核才能生效

---

## 8. 扩展示例

### 8.1 添加新规则

```python
# 通过API添加新规则
rag_service.add_knowledge(
    title="美妆类目规则",
    content="""美妆类目规则：
1. 禁止使用医疗术语：如"治疗"、"疗效"等
2. 需要标注成分：如主要成分、功效成分
3. 注明适用肤质：干性/油性/混合性等
4. 标注保质期：生产日期和保质期
5. 禁止夸大宣传：如"永久美白"等
6. 需要标注产地：国产品牌/进口品牌""",
    category="beauty_rules",
    source="平台规则文档"
)
```

### 8.2 扩展检索接口

```python
def retrieve_with_fallback(self, query, top_k=3):
    """
    带降级方案的检索

    当向量检索失败时，降级为关键词检索

    参数：
        query: 查询文本
        top_k: 返回数量

    返回：
        相似文档列表
    """

    try:
        return self._vector_search(query, top_k)
    except Exception as e:
        # 降级为关键词检索
        return self._keyword_search(query, top_k)
```

### 8.3 批量添加知识

```python
def batch_add_knowledge(self, knowledge_list: List[Dict]):
    """
    批量添加知识

    参数：
        knowledge_list: 知识列表

    返回：
        添加成功的数量
    """

    success_count = 0
    for knowledge in knowledge_list:
        try:
            self.add_knowledge(**knowledge)
            success_count += 1
        except Exception as e:
            # 记录错误但继续处理
            pass

    return success_count
```

---

## 9. 面试亮点

### 9.1 为什么需要RAG？

```
1. LLM知识有限：训练数据截止到特定时间，无法获取最新规则
2. 规则准确性：直接从知识库获取最新规则，避免LLM记错
3. 领域专业性：包含类目特定知识，提升内容专业性
4. 易于更新：规则变更只需更新知识库，无需修改代码
5. 合规要求：电商平台规则严格，需要确保内容合规
```

### 9.2 如何构建知识库？

```
1. 知识分类：按平台规则、类目规则等进行分类
2. 知识采集：从平台规则文档、行业标准等来源采集知识
3. 向量化：使用Sentence Transformers生成向量
4. 存储：存储到数据库，包含向量和元数据
5. 管理：支持新增、修改、删除、禁用等操作
```

### 9.3 如何评估RAG效果？

```
1. 检索准确性：检查检索结果是否与查询相关
2. 生成质量：评估生成内容是否符合规则
3. 合规性：检查生成内容是否存在违规词
4. 用户反馈：收集用户对生成内容的满意度
5. A/B测试：对比有无RAG时的生成效果
```

### 9.4 如果知识库很大，如何优化检索性能？

```
1. 向量库升级：从内存向量库升级到FAISS/Milvus
2. 索引优化：使用IVF、HNSW等索引加速检索
3. 知识分区：按类目进行分区，减少检索范围
4. 缓存机制：缓存高频查询结果
5. 增量更新：只更新新增或变更的知识
```

### 9.5 如何处理知识冲突？

```
1. 版本控制：追踪知识变更历史，支持回滚
2. 优先级机制：新版本知识覆盖旧版本
3. 审核流程：新增知识需经过审核才能生效
4. 冲突检测：检测同一规则的不同版本之间的冲突
5. 人工干预：复杂冲突由人工解决
```

---

## 10. 扩展方向

### 10.1 向量库升级

- [ ] 升级到FAISS本地向量库
- [ ] 支持Milvus/Pinecone分布式向量数据库
- [ ] 添加向量索引优化

### 10.2 检索策略优化

- [ ] 实现语义重排序
- [ ] 支持混合检索（关键词+向量）
- [ ] 添加查询扩展功能

### 10.3 知识管理增强

- [ ] 实现知识自动更新
- [ ] 添加知识版本控制
- [ ] 实现知识审核流程

### 10.4 RAG效果评估

- [ ] 添加检索效果评估指标
- [ ] 实现生成质量评估
- [ ] 支持A/B测试框架
