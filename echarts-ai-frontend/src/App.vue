<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <h1>AI 智能图表生成系统</h1>
        <p>使用自然语言描述和数据，快速生成专业的数据可视化图表</p>
      </div>
    </header>
    
    <main class="container">
      <ChartGenerator />
    </main>
    
    <footer class="app-footer">
      <div class="container">
        <p>&copy; 2025 Emmit AI 智能图表生成系统</p>
      </div>
    </footer>
  </div>
</template>

<script>
import ChartGenerator from './components/ChartGenerator.vue';

export default {
  name: 'App',
  components: {
    ChartGenerator
  }
};
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Poppins', 'Arial', sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f8f9fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.app-header {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  padding: 2.5rem 0;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin-bottom: 0.5rem;
  font-weight: 700;
  font-size: 2.5rem;
  letter-spacing: -0.5px;
}

.app-header p {
  font-size: 1.1rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
}

.app-footer {
  background-color: #343a40;
  color: white;
  padding: 1.5rem 0;
  text-align: center;
  margin-top: 3rem;
}

button {
  transition: all 0.3s ease;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .app-header h1 {
    font-size: 2rem;
  }
  
  .app-header p {
    font-size: 1rem;
  }
}
</style>
