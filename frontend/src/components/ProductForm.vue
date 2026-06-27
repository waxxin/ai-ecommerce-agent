<script setup>
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits(['generate'])

const productName = ref('')
const category = ref('general')
const features = ref('')
const description = ref('')
const loading = ref(false)

const categories = [
  { value: 'general', label: '通用' },
  { value: 'electronics', label: '3C数码' },
  { value: 'clothing', label: '服装' },
  { value: 'beauty', label: '美妆' },
  { value: 'food', label: '食品' },
  { value: 'home', label: '家居' }
]

const handleSubmit = async () => {
  if (!productName.value.trim()) {
    alert('请输入商品名称')
    return
  }

  loading.value = true

  try {
    const featureList = features.value.split('\n').filter(f => f.trim())
    
    const response = await axios.post('/api/v1/generate', {
      user_input: `为商品"${productName.value}"生成电商内容`,
      context: {
        product_name: productName.value,
        category: category.value,
        features: featureList,
        description: description.value
      }
    })

    emit('generate', response.data)
  } catch (error) {
    console.error('生成失败:', error)
    alert('生成失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="product-form">
    <h2 class="form-title">商品信息输入</h2>
    
    <el-form label-width="120px" class="form-content">
      <el-form-item label="商品名称" required>
        <el-input 
          v-model="productName" 
          placeholder="请输入商品名称，如：无线蓝牙耳机" 
          size="large"
        />
      </el-form-item>
      
      <el-form-item label="商品类目">
        <el-select v-model="category" placeholder="请选择类目" size="large">
          <el-option v-for="cat in categories" :key="cat.value" :label="cat.label" :value="cat.value" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="商品特点">
        <el-input 
          v-model="features" 
          type="textarea" 
          placeholder="每行一个特点，如：\n降噪功能\n蓝牙5.0\n超长续航" 
          :rows="3"
        />
      </el-form-item>
      
      <el-form-item label="商品描述">
        <el-input 
          v-model="description" 
          type="textarea" 
          placeholder="请输入商品详细描述" 
          :rows="4"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button 
          type="primary" 
          size="large" 
          :loading="loading"
          @click="handleSubmit"
          class="submit-btn"
        >
          {{ loading ? '生成中...' : '生成内容' }}
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>
.product-form {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
}

.form-title {
  font-size: 1.3rem;
  margin-bottom: 20px;
  color: #333;
}

.form-content {
  max-width: 600px;
}

.submit-btn {
  width: 100%;
}

.el-input, .el-select, .el-textarea {
  width: 100%;
}
</style>