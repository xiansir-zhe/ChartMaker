import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'

// 配置axios默认值
axios.defaults.baseURL = 'http://localhost:8000'

const app = createApp(App)
app.mount('#app')
