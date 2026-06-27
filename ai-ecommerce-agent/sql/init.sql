-- AI E-commerce Agent Database Schema
-- Version: 1.0.0
-- Created: 2024

-- Create database
CREATE DATABASE IF NOT EXISTS ai_ecommerce DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ai_ecommerce;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Prompt templates table
CREATE TABLE IF NOT EXISTS prompt_templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(500),
    template_type VARCHAR(50),
    content TEXT NOT NULL,
    variables JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_template_type (template_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Generation history table
CREATE TABLE IF NOT EXISTS generation_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    product_name VARCHAR(200),
    category VARCHAR(100),
    features JSON,
    input_text TEXT,
    output_data JSON,
    prompt_id INT,
    model_name VARCHAR(100),
    status VARCHAR(20),
    input_tokens INT DEFAULT 0,
    output_tokens INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    latency_ms INT DEFAULT 0,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- AI logs table
CREATE TABLE IF NOT EXISTS ai_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    model_name VARCHAR(100),
    prompt TEXT,
    response TEXT,
    status VARCHAR(20),
    error_message TEXT,
    latency_ms INT DEFAULT 0,
    input_tokens INT DEFAULT 0,
    output_tokens INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    extra_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_model_name (model_name),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Knowledge base table
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    source VARCHAR(200),
    embedding JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Model configuration table
CREATE TABLE IF NOT EXISTS model_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model_name VARCHAR(100) NOT NULL UNIQUE,
    provider VARCHAR(50),
    model_id VARCHAR(100),
    api_key VARCHAR(255),
    api_base_url VARCHAR(255),
    temperature FLOAT DEFAULT 0.7,
    max_tokens INT DEFAULT 2048,
    top_p FLOAT DEFAULT 0.9,
    enabled BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_model_name (model_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert initial data
-- Prompt templates
INSERT IGNORE INTO prompt_templates (name, description, template_type, content, variables) VALUES
('title_generation', '生成多平台商品标题', 'title', '你是一个专业的电商运营助手。\n\n商品信息：\n- 商品名称：{{product_name}}\n- 商品特点：{{features}}\n\n{{rules_context}}\n\n任务：请为以下平台生成商品标题\n\n要求：\n- 拼多多标题：30字以内，包含核心关键词，突出性价比\n- 淘宝标题：60字以内，包含营销词，吸引点击\n- 小红书标题：吸引眼球，带话题标签\n\n请严格按照以下JSON格式输出：\n{\n  "pdd": "拼多多标题",\n  "tb": "淘宝标题",\n  "xhs": "小红书标题"\n}', '{"product_name": "商品名称", "features": "商品特点", "rules_context": "规则上下文"}'),
('selling_points_extraction', '提取商品核心卖点', 'feature', '你是一个专业的电商运营助手。\n\n商品信息：\n- 商品名称：{{product_name}}\n- 商品特点：{{features}}\n- 商品描述：{{description}}\n\n任务：提取商品的核心卖点\n\n要求：\n- 提取5-8个核心卖点\n- 每个卖点不超过20字\n- 突出产品优势和差异化\n\n请严格按照以下JSON格式输出：\n{\n  "selling_points": ["卖点1", "卖点2", "卖点3"]\n}', '{"product_name": "商品名称", "features": "商品特点", "description": "商品描述"}'),
('faq_generation', '生成客服常见问题', 'faq', '你是一个专业的电商运营助手。\n\n商品信息：\n- 商品名称：{{product_name}}\n- 商品特点：{{features}}\n\n任务：生成客服常见问题及答案\n\n要求：\n- 生成3-5个常见问题\n- 问题和答案要实用\n- 符合电商客服场景\n\n请严格按照以下JSON格式输出：\n{\n  "faq": [\n    {"question": "问题1", "answer": "答案1"},\n    {"question": "问题2", "answer": "答案2"}\n  ]\n}', '{"product_name": "商品名称", "features": "商品特点"}');

-- Knowledge base
INSERT IGNORE INTO knowledge_base (title, content, category) VALUES
('拼多多标题规范', '拼多多标题规范：\n1. 标题长度控制在20-30字\n2. 必须包含核心关键词\n3. 可以使用营销词如：包邮、特价、限时\n4. 禁止使用夸大词汇\n5. 不要重复关键词', 'title_rules'),
('淘宝标题规范', '淘宝标题规范：\n1. 标题长度控制在50-60字\n2. 包含核心关键词和长尾词\n3. 使用营销词提高点击率\n4. 按照"品牌+核心词+属性词+营销词"结构\n5. 避免堆砌关键词', 'title_rules'),
('小红书标题规范', '小红书标题规范：\n1. 标题要吸引人，使用emoji\n2. 包含话题标签，如#好物推荐\n3. 使用数字增加可信度\n4. 营造紧迫感或好奇心\n5. 字数控制在20-30字', 'title_rules'),
('3C数码类目规则', '3C数码类目规则：\n1. 必须标注品牌和型号\n2. 说明产品规格参数\n3. 突出产品性能特点\n4. 可以强调售后服务\n5. 注明保修期限', 'electronics_rules'),
('服装类目规则', '服装类目规则：\n1. 标注材质和尺码\n2. 说明适用季节\n3. 突出设计亮点\n4. 可以使用模特展示\n5. 注明洗涤方式', 'clothing_rules');

-- Model configurations
INSERT IGNORE INTO model_config (model_name, provider, model_id, api_base_url, temperature, max_tokens, enabled) VALUES
('qwen-max', 'alibaba', 'qwen-max', 'https://dashscope.aliyuncs.com/compatible-mode/v1', 0.7, 2048, TRUE),
('deepseek-chat', 'deepseek', 'deepseek-chat', 'https://api.deepseek.com/v1', 0.7, 2048, TRUE);