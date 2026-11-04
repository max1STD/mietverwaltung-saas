import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import './styles/main.css'

const app = createApp({})
app.use(createPinia())
app.use(router)
app.mount('#app')
