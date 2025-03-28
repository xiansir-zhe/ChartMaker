<template>
  <div class="data-analysis">
    <div class="analysis-header">
      <h3>数据分析</h3>
      <button 
        @click="analyzeData" 
        class="btn btn-info"
        :disabled="!data || isLoading"
      >
        <span v-if="isLoading" class="loader"></span>
        {{ isLoading ? '分析中...' : '分析数据' }}
      </button>
    </div>
    
    <div v-if="analysis" class="analysis-results">
      <div v-if="analysis.statistics" class="analysis-card">
        <div class="analysis-card-header">
          <h4>基本统计信息</h4>
          <i class="icon">📊</i>
        </div>
        <div class="analysis-card-body">
          <pre>{{ JSON.stringify(analysis.statistics, null, 2) }}</pre>
        </div>
      </div>
      
      <div v-if="analysis.trends" class="analysis-card">
        <div class="analysis-card-header">
          <h4>主要趋势</h4>
          <i class="icon">📈</i>
        </div>
        <div class="analysis-card-body">
          <p>{{ analysis.trends }}</p>
        </div>
      </div>
      
      <div v-if="analysis.recommended_charts" class="analysis-card">
        <div class="analysis-card-header">
          <h4>推荐图表</h4>
          <i class="icon">🎯</i>
        </div>
        <div class="analysis-card-body">
          <ul class="recommendation-list">
            <li v-for="(chart, index) in analysis.recommended_charts" :key="index" class="recommendation-item">
              <div class="recommendation-type">{{ chart.type }}</div>
              <div class="recommendation-reason">{{ chart.reason }}</div>
            </li>
          </ul>
        </div>
      </div>
      
      <div v-if="analysis.observations" class="analysis-card">
        <div class="analysis-card-header">
          <h4>其他观察</h4>
          <i class="icon">🔍</i>
        </div>
        <div class="analysis-card-body">
          <p>{{ analysis.observations }}</p>
        </div>
      </div>
    </div>
    
    <div v-if="!analysis && !isLoading && !error" class="analysis-placeholder">
      <i class="icon large">📊</i>
      <p>点击"分析数据"按钮，获取数据洞察</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    data: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      analysis: null,
      isLoading: false,
      error: null
    };
  },
  methods: {
    async analyzeData() {
      if (!this.data) {
        this.error = '没有数据可分析';
        return;
      }
      
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.post('/analyze-data', {
          data: this.data
        });
        
        this.analysis = response.data.analysis;
        
        if (this.analysis.raw_text) {
          this.error = '无法解析分析结果';
        }
        
        this.$emit('analysis-complete', this.analysis);
      } catch (error) {
        this.error = '分析数据时出错: ' + (error.response?.data?.detail || error.message);
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.data-analysis {
  padding: 0.5rem;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.analysis-header h3 {
  margin: 0;
  font-weight: 600;
  color: #333;
}

.btn-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #00c6fb 0%, #005bea 100%);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-info:hover {
  box-shadow: 0 5px 15px rgba(0, 91, 234, 0.3);
  transform: translateY(-2px);
}

.btn-info:disabled {
  background: #cccccc;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.analysis-results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.analysis-card {
  background-color: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.analysis-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.analysis-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  color: #333;
}

.analysis-card-header h4 {
  margin: 0;
  font-weight: 600;
  font-size: 1.1rem;
}

.analysis-card-body {
  padding: 1rem;
}

.analysis-card-body pre {
  background-color: #f8f9fa;
  padding: 0.75rem;
  border-radius: 8px;
  overflow: auto;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
}

.recommendation-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.recommendation-item {
  padding: 0.75rem;
  border-bottom: 1px solid #eee;
}

.recommendation-item:last-child {
  border-bottom: none;
}

.recommendation-type {
  font-weight: 600;
  color: #2575fc;
  margin-bottom: 0.25rem;
}

.recommendation-reason {
  font-size: 0.9rem;
  color: #666;
}

.analysis-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background-color: #f8f9fa;
  border-radius: 12px;
  text-align: center;
}

.icon {
  font-style: normal;
}

.icon.large {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-message {
  padding: 1rem;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 8px;
  margin-top: 1rem;
}

.loader {
  display: inline-block;
  width: 1.25rem;
  height: 1.25rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .analysis-results {
    grid-template-columns: 1fr;
  }
  
  .analysis-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .btn-info {
    width: 100%;
    justify-content: center;
  }
}
</style> 