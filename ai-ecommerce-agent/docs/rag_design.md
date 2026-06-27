# RAG设计说明

## 1. RAG概述

RAG（Retrieval-Augmented Generation）是一种将检索与生成相结合的AI技术。在本系统中，RAG用于在生成电商内容前，从知识库中检索相关的平台规则和类目规范，从而提高生成内容的质量和合规性。

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

## 3. 知识库结构

### 3.1 知识分类

| 分类 | 内容 | 用途 |
|------|------|------|
| `title_rules` | 各平台标题规范 | 标题生成时注入规则 |
| `electronics_rules` | 3C数码类目规则 | 3C商品生成时注入 |
| `clothing_rules` | 服装类目规则 | 服装商品生成时注入 |
| `beauty_rules` | 美妆类目规则 | 美妆商品生成时注入 |
| `food_rules` | 食品类目规则 | 食品商品生成时注入 |
| `home_rules` | 家居类目规则 | 家居商品生成时注入 |

### 3.2 知识库数据表

```sql
CREATE TABLE knowledge_base (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,    -- 知识标题
    content TEXT NOT NULL,          -- 知识内容
    category VARCHAR(100),          -- 知识分类
    source VARCHAR(200),            -- 来源
    embedding JSON,                 -- 向量化结果
    is_active BOOLEAN DEFAULT TRUE, -- 是否启用
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 4. 核心实现

### 4.1 Embedding生成

```python
def _compute_embedding(self, text: str) -> List[float]:
    """使用Sentence Transformers生成文本向量"""
    if not self.embedding_model:
        return [0.0] * 384  # 384维向量
    
    return self.embedding_model.encode(text).tolist()
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
    """
    query_embedding = self._compute_embedding(query)
    
    results = []
    for item_id, item_data in self.vector_store.items():
        similarity = self._cosine_similarity(query_embedding, item_data["embedding"])
        if similarity > 0.3:  # 相似度阈值
            results.append({
                "id": item_id,
                "title": item_data["title"],
                "content": item_data["content"],
                "similarity": round(similarity, 4)
            })
    
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]
```

### 4.3 规则增强

```python
def get_rules_for_category(self, category: str) -> str:
    """获取指定类目的规则"""
    # 1. 获取标题规范
    title_rules = self.get_rules("title_rules")
    
    # 2. 获取类目规则
    category_rules = self.get_rules(f"{category}_rules")
    
    # 3. 拼接成上下文
    return f"【标题规范】\n{title_rules}\n\n【类目规则】\n{category_rules}"
```

## 5. 在Agent中的应用

```python
def run(self, user_input, context):
    # Step 1: 规划任务
    plan = self._plan(user_input, context)
    
    # Step 2: 判断是否需要RAG
    rules_context = ""
    if plan["requires_rag"]:
        rules_context = self._retrieve_rules(plan["category"])
    
    # Step 3: 执行步骤（规则已注入Prompt）
    for step in plan["steps"]:
        prompt = f"""任务：{step['description']}
        
{rules_context}

商品信息：{context}"""
        result = llm_service.call_structured(prompt, step["schema"])
```

## 6. RAG效果

### 6.1 无RAG时的问题

- 生成的标题可能不符合平台规范
- 可能使用违规词汇
- 缺乏类目特定的专业知识

### 6.2 RAG增强后的效果

- **合规性提升**: 标题符合各平台规则
- **质量提升**: 包含类目特定的专业描述
- **一致性**: 同类商品描述风格统一
- **可维护性**: 规则变更只需更新知识库，无需修改代码

## 7. 优化方向

### 7.1 向量库升级

| 阶段 | 方案 | 适用场景 |
|------|------|----------|
| 当前 | 内存向量库 | 小型知识库(<1000条) |
| 中级 | FAISS | 中型知识库(1000-10000条) |
| 高级 | Milvus/Pinecone | 大型知识库(>10000条) |

### 7.2 检索策略优化

1. **语义重排序**: 对检索结果进行语义排序
2. **多跳检索**: 支持复杂问题的多步推理
3. **混合检索**: 结合关键词检索和向量检索

### 7.3 知识管理

1. **自动更新**: 定期从外部源更新知识库
2. **版本控制**: 追踪知识变更历史
3. **过期淘汰**: 自动清理过期知识

## 8. 扩展示例

### 8.1 添加新规则

```python
# 通过API添加
rag_service.add_knowledge(
    title="美妆类目规则",
    content="""美妆类目规则：
1. 禁止使用医疗术语
2. 需要标注成分
3. 注明适用肤质
4. 标注保质期
5. 禁止夸大宣传""",
    category="beauty_rules"
)
```

### 8.2 扩展检索接口

```python
def retrieve_with_fallback(self, query, top_k=3):
    """带降级方案的检索"""
    try:
        return self._vector_search(query, top_k)
    except Exception:
        return self._keyword_search(query, top_k)
```