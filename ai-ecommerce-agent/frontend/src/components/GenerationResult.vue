<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['refresh'])

const titles = computed(() => props.data.titles || {})
const sellingPoints = computed(() => props.data.selling_points || [])
const faq = computed(() => props.data.faq || [])
const stats = computed(() => props.data.execution_stats || {})
</script>

<template>
  <div class="generation-result">
    <h2 class="result-title">生成结果</h2>
    
    <div class="stats-row">
      <el-statistic title="总耗时" :value="stats.total_latency_ms" suffix="ms" />
      <el-statistic title="执行步骤" :value="stats.step_count" suffix="步" />
      <el-statistic title="成功步骤" :value="stats.success_steps" suffix="步" />
    </div>
    
    <div class="result-sections">
      <div class="section">
        <h3 class="section-title">多平台标题</h3>
        
        <div class="title-cards">
          <div class="title-card pdd">
            <div class="title-platform">拼多多</div>
            <div class="title-content">{{ titles.pdd }}</div>
          </div>
          
          <div class="title-card tb">
            <div class="title-platform">淘宝</div>
            <div class="title-content">{{ titles.tb }}</div>
          </div>
          
          <div class="title-card xhs">
            <div class="title-platform">小红书</div>
            <div class="title-content">{{ titles.xhs }}</div>
          </div>
        </div>
      </div>
      
      <div class="section">
        <h3 class="section-title">核心卖点</h3>
        
        <div class="selling-points">
          <el-tag 
            v-for="(point, index) in sellingPoints" 
            :key="index" 
            type="success" 
            size="large"
            class="point-tag"
          >
            {{ point }}
          </el-tag>
        </div>
      </div>
      
      <div class="section">
        <h3 class="section-title">客服FAQ</h3>
        
        <div class="faq-list">
          <div v-for="(item, index) in faq" :key="index" class="faq-item">
            <div class="faq-question">
              <el-icon><HelpFilled /></el-icon>
              {{ item.question }}
            </div>
            <div class="faq-answer">{{ item.answer }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="result-actions">
      <el-button type="primary" @click="emit('refresh')">
        <el-icon><Refresh /></el-icon>
        重新生成
      </el-button>
      <el-button @click="copyAll">
        <el-icon><CopyDocument /></el-icon>
        复制全部
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.generation-result {
  margin-top: 24px;
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
}

.result-title {
  font-size: 1.3rem;
  margin-bottom: 20px;
  color: #333;
}

.stats-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.result-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  background: white;
  padding: 20px;
  border-radius: 8px;
}

.section-title {
  font-size: 1.1rem;
  margin-bottom: 16px;
  color: #666;
  border-bottom: 2px solid #eee;
  padding-bottom: 8px;
}

.title-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.title-card {
  padding: 16px;
  border-radius: 8px;
  background: #f5f5f5;
}

.title-card.pdd {
  border-left: 4px solid #e02e24;
}

.title-card.tb {
  border-left: 4px solid #ff5000;
}

.title-card.xhs {
  border-left: 4px solid #ff2442;
}

.title-platform {
  font-size: 0.9rem;
  font-weight: bold;
  margin-bottom: 8px;
  color: #666;
}

.title-content {
  font-size: 1rem;
  color: #333;
  line-height: 1.5;
}

.selling-points {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.point-tag {
  margin-bottom: 8px;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.faq-item {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 6px;
}

.faq-question {
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.faq-answer {
  color: #666;
  line-height: 1.6;
}

.result-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}

.el-statistic {
  flex: 1;
  text-align: center;
}
</style>