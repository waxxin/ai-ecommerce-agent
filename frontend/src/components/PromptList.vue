<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const templates = ref([])
const loading = ref(true)

const fetchPrompts = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/prompts')
    templates.value = response.data.templates
  } catch (error) {
    console.error('获取Prompt模板失败:', error)
  } finally {
    loading.value = false
  }
}

const formatVariables = (variables) => {
  if (!variables) return '无'
  return Object.keys(variables).join(', ')
}

onMounted(fetchPrompts)
</script>

<template>
  <div class="prompt-list">
    <h2 class="list-title">Prompt模板管理</h2>
    
    <el-table :data="templates" :loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="模板名称" min-width="150" />
      <el-table-column prop="description" label="描述" min-width="200" />
      <el-table-column prop="template_type" label="类型" width="120">
        <template #default="scope">
          <el-tag size="small" type="info">{{ scope.row.template_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="variables" label="变量" width="200">
        <template #default="scope">
          {{ formatVariables(scope.row.variables) }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="scope">
          {{ new Date(scope.row.created_at).toLocaleString('zh-CN') }}
        </template>
      </el-table-column>
    </el-table>
    
    <div class="prompt-info">
      <h3>Prompt模板说明</h3>
      <ul>
        <li><strong>title_generation</strong>: 生成多平台商品标题（拼多多、淘宝、小红书）</li>
        <li><strong>selling_points_extraction</strong>: 提取商品核心卖点</li>
        <li><strong>faq_generation</strong>: 生成客服常见问题及答案</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.prompt-list {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
}

.list-title {
  font-size: 1.3rem;
  margin-bottom: 20px;
  color: #333;
}

.prompt-info {
  margin-top: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
}

.prompt-info h3 {
  font-size: 1.1rem;
  margin-bottom: 12px;
  color: #666;
}

.prompt-info ul {
  list-style: none;
  padding: 0;
}

.prompt-info li {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
  color: #333;
}

.prompt-info li:last-child {
  border-bottom: none;
}
</style>