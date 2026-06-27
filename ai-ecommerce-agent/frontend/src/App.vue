<script setup>import { ref } from 'vue';
import ProductForm from './components/ProductForm.vue';
import GenerationResult from './components/GenerationResult.vue';
import HistoryList from './components/HistoryList.vue';
import PromptList from './components/PromptList.vue';
const activeTab = ref('generate');
const generatedData = ref(null);
const handleGenerate = (data) => {
 generatedData.value = data;
};
const handleRefresh = () => {
 generatedData.value = null;
};
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <h1>AI电商内容生成系统</h1>
      <p>基于LLM的智能电商内容创作平台</p>
    </header>
    
    <main class="app-main">
      <el-tabs v-model="activeTab" type="border-card" class="main-tabs">
        <el-tab-pane label="AI生成" name="generate">
          <ProductForm @generate="handleGenerate" />
          <GenerationResult v-if="generatedData" :data="generatedData" @refresh="handleRefresh" />
        </el-tab-pane>
        
        <el-tab-pane label="历史记录" name="history">
          <HistoryList />
        </el-tab-pane>
        
        <el-tab-pane label="Prompt管理" name="prompts">
          <PromptList />
        </el-tab-pane>
      </el-tabs>
    </main>
    
    <footer class="app-footer">
      <p>AI E-commerce Agent © 2024</p>
    </footer>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  text-align: center;
  padding: 30px 20px;
  color: white;
}

.app-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
}

.app-header p {
  font-size: 1.1rem;
  opacity: 0.9;
}

.app-main {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.main-tabs {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.app-footer {
  text-align: center;
  padding: 20px;
  color: white;
  opacity: 0.8;
}

.app-footer p {
  font-size: 0.9rem;
}

.el-tabs__header {
  margin: 0;
  background: #f8f9fa;
}

.el-tabs__content {
  padding: 24px;
}
</style>