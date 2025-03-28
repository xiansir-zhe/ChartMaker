<template>
  <div class="chart-generator">
    <div class="card input-section">
      <h2>创建你的图表</h2>
      
      <div class="form-group">
        <label for="description">图表描述</label>
        <textarea 
          id="description"
          v-model="description" 
          placeholder="请输入您想要的图表描述，例如：'创建一个显示2020-2023年各季度销售额的折线图'"
          rows="3"
          class="form-control"
        ></textarea>
      </div>
      
      <div class="form-group">
        <label>数据来源</label>
        <div class="data-source-options">
          <div class="upload-container">
            <label for="file-upload" class="file-upload-label">
              <i class="icon">📁</i>
              <span>上传数据文件</span>
              <small>(JSON/CSV)</small>
            </label>
            <input 
              id="file-upload"
              type="file" 
              @change="handleFileUpload" 
              accept=".json,.csv"
              class="file-input"
            />
          </div>
          
          <div class="divider">或</div>
          
          <button @click="useExampleData" class="btn btn-outline">
            <i class="icon">📊</i>
            使用示例数据
          </button>
        </div>
      </div>
      
      <div v-if="data" class="data-preview">
        <div class="data-preview-header">
          <h3>数据预览</h3>
          <span class="data-count">{{ data.length }} 条数据</span>
        </div>
        <pre>{{ dataPreview }}</pre>
      </div>
      
      <button 
        @click="generateChart" 
        class="btn btn-primary generate-btn"
        :disabled="!description || !data || isLoading"
      >
        <span v-if="isLoading" class="loader"></span>
        <span>{{ isLoading ? '生成中...' : '生成图表' }}</span>
      </button>
    </div>
    
    <div v-if="chartConfig" class="card result-section">
      <div class="tabs">
        <button 
          @click="activeTab = 'chart'" 
          :class="{ active: activeTab === 'chart' }"
          class="tab-btn"
        >
          图表预览
        </button>
        <button 
          @click="activeTab = 'config'" 
          :class="{ active: activeTab === 'config' }"
          class="tab-btn"
        >
          配置代码
        </button>
        <button 
          @click="activeTab = 'editor'" 
          :class="{ active: activeTab === 'editor' }"
          class="tab-btn"
        >
          配置编辑器
        </button>
        <button 
          @click="activeTab = 'analysis'" 
          :class="{ active: activeTab === 'analysis' }"
          class="tab-btn"
        >
          数据分析
        </button>
      </div>
      
      <div v-if="activeTab === 'chart'" class="chart-container">
        <div ref="chartContainer" style="width: 100%; height: 400px;"></div>
        <div class="chart-actions">
          <button @click="downloadChart" class="btn btn-sm">
            <i class="icon">💾</i> 下载图表
          </button>
          <button @click="fullscreenChart" class="btn btn-sm">
            <i class="icon">🔍</i> 全屏查看
          </button>
        </div>
      </div>
      
      <div v-if="activeTab === 'config'" class="config-container">
        <div class="code-header">
          <span>ECharts 配置</span>
          <button @click="copyConfig" class="btn btn-sm">
            <i class="icon">📋</i> 复制配置
          </button>
        </div>
        <pre class="code-block">{{ JSON.stringify(chartConfig, null, 2) }}</pre>
      </div>
      
      <div v-if="activeTab === 'editor'" class="editor-container">
        <textarea 
          v-model="editableConfig" 
          rows="15" 
          class="form-control code-editor"
          spellcheck="false"
        ></textarea>
        <button @click="applyConfigChanges" class="btn btn-primary">
          应用更改
        </button>
      </div>
      
      <div v-if="activeTab === 'analysis'" class="analysis-container">
        <DataAnalysis 
          :data="data" 
          @analysis-complete="onAnalysisComplete"
        />
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      <i class="icon">⚠️</i>
      <p>{{ error }}</p>
      <button @click="error = null" class="close-btn">×</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';
import DataAnalysis from './DataAnalysis.vue';

export default {
  components: {
    DataAnalysis
  },
  data() {
    return {
      description: '',
      data: null,
      chartConfig: null,
      editableConfig: '',
      chart: null,
      isLoading: false,
      error: null,
      activeTab: 'chart',
      analysisResult: null,
      exampleData: [
        { year: '2020', quarter: 'Q1', sales: 1254 },
        { year: '2020', quarter: 'Q2', sales: 1528 },
        { year: '2020', quarter: 'Q3', sales: 1867 },
        { year: '2020', quarter: 'Q4', sales: 2385 },
        { year: '2021', quarter: 'Q1', sales: 1587 },
        { year: '2021', quarter: 'Q2', sales: 2175 },
        { year: '2021', quarter: 'Q3', sales: 2436 },
        { year: '2021', quarter: 'Q4', sales: 3127 },
        { year: '2022', quarter: 'Q1', sales: 2248 },
        { year: '2022', quarter: 'Q2', sales: 2734 },
        { year: '2022', quarter: 'Q3', sales: 3015 },
        { year: '2022', quarter: 'Q4', sales: 3756 },
        { year: '2023', quarter: 'Q1', sales: 2614 },
        { year: '2023', quarter: 'Q2', sales: 3185 },
        { year: '2023', quarter: 'Q3', sales: 3428 },
        { year: '2023', quarter: 'Q4', sales: 4125 }
      ]
    };
  },
  computed: {
    dataPreview() {
      if (!this.data) return '';
      return JSON.stringify(this.data.slice(0, 3), null, 2) + 
        (this.data.length > 3 ? '\n...' : '');
    }
  },
  methods: {
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          if (file.name.endsWith('.json')) {
            this.data = JSON.parse(e.target.result);
          } else if (file.name.endsWith('.csv')) {
            this.data = this.parseCSV(e.target.result);
          }
          this.error = null;
        } catch (error) {
          this.error = '文件解析错误: ' + error.message;
        }
      };
      
      if (file.name.endsWith('.json') || file.name.endsWith('.csv')) {
        reader.readAsText(file);
      } else {
        this.error = '不支持的文件格式。请上传 JSON 或 CSV 文件。';
      }
    },
    
    parseCSV(csvText) {
      const lines = csvText.split('\n');
      const headers = lines[0].split(',').map(h => h.trim());
      
      return lines.slice(1).filter(line => line.trim()).map(line => {
        const values = line.split(',').map(v => v.trim());
        const row = {};
        
        headers.forEach((header, index) => {
          // 尝试将数值转换为数字
          const value = values[index];
          row[header] = isNaN(value) ? value : Number(value);
        });
        
        return row;
      });
    },
    
    useExampleData() {
      this.data = this.exampleData;
      this.error = null;
    },
    
    async generateChart() {
      if (!this.description || !this.data) {
        this.error = '请提供图表描述和数据';
        return;
      }
      
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.post('/generate-chart-config', {
          description: this.description,
          data: this.data,
        });
        
        this.chartConfig = response.data.config;
        
        if (this.chartConfig.raw_text) {
          this.error = '无法生成有效的图表配置。请尝试修改您的描述。';
          this.activeTab = 'config';
        } else {
          this.editableConfig = JSON.stringify(this.chartConfig, null, 2);
          this.activeTab = 'chart';
          this.$nextTick(() => {
            this.renderChart();
          });
        }
      } catch (error) {
        this.error = '生成图表时出错: ' + (error.response?.data?.detail || error.message);
      } finally {
        this.isLoading = false;
      }
    },
    
    renderChart() {
      if (this.chart) {
        this.chart.dispose();
      }
      
      this.chart = echarts.init(this.$refs.chartContainer);
      
      try {
        this.chart.setOption(this.chartConfig);
      } catch (error) {
        this.error = '渲染图表时出错: ' + error.message;
      }
    },
    
    copyConfig() {
      navigator.clipboard.writeText(JSON.stringify(this.chartConfig, null, 2))
        .then(() => {
          alert('配置已复制到剪贴板');
        })
        .catch(err => {
          this.error = '复制失败: ' + err.message;
        });
    },
    
    applyConfigChanges() {
      try {
        this.chartConfig = JSON.parse(this.editableConfig);
        this.activeTab = 'chart';
        this.$nextTick(() => {
          this.renderChart();
        });
        this.error = null;
      } catch (error) {
        this.error = 'JSON 解析错误: ' + error.message;
      }
    },
    
    downloadChart() {
      if (!this.chart) return;
      
      const url = this.chart.getDataURL({
        pixelRatio: 2,
        backgroundColor: '#fff'
      });
      
      const link = document.createElement('a');
      link.download = '图表_' + new Date().getTime() + '.png';
      link.href = url;
      link.click();
    },
    
    fullscreenChart() {
      const chartContainer = this.$refs.chartContainer;
      
      if (!chartContainer) return;
      
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        chartContainer.requestFullscreen();
      }
    },
    
    onAnalysisComplete(analysis) {
      this.analysisResult = analysis;
    }
  },
  watch: {
    activeTab(newTab) {
      if (newTab === 'chart') {
        this.$nextTick(() => {
          this.renderChart();
        });
      }
    }
  },
  mounted() {
    window.addEventListener('resize', () => {
      if (this.chart) {
        this.chart.resize();
      }
    });
    
    document.addEventListener('fullscreenchange', () => {
      if (this.chart) {
        this.chart.resize();
      }
    });
  },
  unmounted() {
    window.removeEventListener('resize', () => {
      if (this.chart) {
        this.chart.resize();
      }
    });
    
    document.removeEventListener('fullscreenchange', () => {
      if (this.chart) {
        this.chart.resize();
      }
    });
    
    if (this.chart) {
      this.chart.dispose();
    }
  }
};
</script>

<style scoped>
.chart-generator {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
}

.card {
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  background-color: #fff;
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.input-section h2, .result-section h2 {
  margin-bottom: 1.5rem;
  color: #333;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: #6a11cb;
  box-shadow: 0 0 0 3px rgba(106, 17, 203, 0.1);
}

.data-source-options {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.upload-container {
  flex: 1;
}

.file-upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.file-upload-label:hover {
  border-color: #6a11cb;
  background-color: rgba(106, 17, 203, 0.05);
}

.file-input {
  display: none;
}

.divider {
  color: #888;
  font-weight: 500;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-outline {
  background-color: transparent;
  border: 2px solid #e0e0e0;
  color: #555;
}

.btn-outline:hover {
  border-color: #6a11cb;
  color: #6a11cb;
}

.btn-primary {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
}

.btn-primary:hover {
  box-shadow: 0 5px 15px rgba(106, 17, 203, 0.3);
}

.btn-primary:disabled {
  background: #cccccc;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.generate-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 1rem;
}

.icon {
  font-style: normal;
  margin-right: 0.5rem;
}

.data-preview {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  max-height: 200px;
  overflow: auto;
}

.data-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.data-count {
  font-size: 0.875rem;
  color: #666;
  background-color: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.tabs {
  display: flex;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  overflow-x: auto;
  scrollbar-width: none;
}

.tabs::-webkit-scrollbar {
  display: none;
}

.tab-btn {
  padding: 0.75rem 1.25rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: #666;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
}

.tab-btn.active {
  border-bottom: 2px solid #6a11cb;
  color: #6a11cb;
  font-weight: 600;
}

.chart-container, .config-container, .editor-container, .analysis-container {
  margin-top: 1rem;
}

.chart-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.code-block {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0 0 8px 8px;
  overflow: auto;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
}

.code-editor {
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  resize: vertical;
}

.error-message {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  align-items: center;
  padding: 1rem;
  background-color: #fff;
  color: #e53935;
  border-left: 4px solid #e53935;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  z-index: 1000;
}

.error-message p {
  margin: 0 1rem 0 0.5rem;
  flex: 1;
}

.close-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 1.25rem;
  cursor: pointer;
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
  .chart-generator {
    padding: 1rem;
  }
  
  .data-source-options {
    flex-direction: column;
  }
  
  .upload-container {
    width: 100%;
  }
  
  .divider {
    margin: 0.5rem 0;
  }
  
  .tabs {
    padding-bottom: 0.5rem;
  }
  
  .tab-btn {
    padding: 0.5rem 1rem;
  }
}
</style> 