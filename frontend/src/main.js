import { createApp } from 'vue'
import App from './App.vue'
import router from './router' 

// XÓA HOẶC COMMENT DÒNG NÀY ĐI
// import './style.css' 
// import './login.css'

const app = createApp(App)

app.use(router)

app.mount('#app')