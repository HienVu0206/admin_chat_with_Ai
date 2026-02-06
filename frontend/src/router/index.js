import { createRouter, createWebHistory } from 'vue-router'
// Dùng ../ để trỏ ra ngoài thư mục router, rồi vào thư mục views
import Login from '../views/Login.vue' 
import Dashboard from '../views/Dashboard.vue'

const routes = [
    { 
        path: '/', 
        redirect: '/login' 
    },
    { 
        path: '/login', 
        name: 'Login', 
        component: Login 
    },
    { 
        path: '/dashboard', 
        name: 'Dashboard', 
        component: Dashboard 
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation Guard (Giữ lại logic bảo vệ route)
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('access_token')
    if (to.path === '/dashboard' && !token) {
        next('/login')
    } else {
        next()
    }
})

// --- QUAN TRỌNG NHẤT LÀ DÒNG NÀY ---
export default router