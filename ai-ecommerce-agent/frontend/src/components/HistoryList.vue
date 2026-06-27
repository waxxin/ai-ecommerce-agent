<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const records = ref([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = 10

const fetchHistory = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/history', {
      params: {
        limit: pageSize,
        offset: (currentPage.value - 1) * pageSize
      }
    })
    records.value = response.data.records
  } catch (error) {
    console.error('获取历史记录失败:', error)
  } finally {
    loading.value = false
  }
}

const deleteRecord = async (id) => {
  if (!confirm('确定要删除这条记录吗？')) return
  
  try {
    await axios.delete(`/api/v1/history/${id}`)
    fetchHistory()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN')
}

onMounted(fetchHistory)
</script>

<template>
  <div class="history-list">
    <h2 class="list-title">生成历史记录</h2>
    
    <el-table :data="records" :loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="product_name" label="商品名称" min-width="150" />
      <el-table-column prop="category" label="类目" width="100">
        <template #default="scope">
          <el-tag size="small">{{ scope.row.category }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="model_name" label="模型" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'" size="small">
            {{ scope.row.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="total_tokens" label="Token消耗" width="120" />
      <el-table-column prop="latency_ms" label="耗时(ms)" width="120" />
      <el-table-column prop="created_at" label="时间" width="180">
        <template #default="scope">
          {{ formatTime(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button size="small" @click="deleteRecord(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination
      v-if="records.length > 0"
      class="pagination"
      layout="prev, pager, next"
      :current-page="currentPage"
      :page-size="pageSize"
      @current-change="currentPage = $event; fetchHistory()"
    />
  </div>
</template>

<style scoped>
.history-list {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
}

.list-title {
  font-size: 1.3rem;
  margin-bottom: 20px;
  color: #333;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}
</style>