import { createRouter, createWebHistory } from 'vue-router'
// Dùng ../ để trỏ ra ngoài thư mục router, rồi vào thư mục views
import Login from '../views/Login.vue' 
import Dashboard from '../views/Dashboard.vue'
// 1. BỔ SUNG IMPORT TRANG AUDIT LOGS
import AuditLogs from '../views/audit-logs.vue' 
import UserManager from '../views/user-manager.vue'

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
    },
    // 2. BỔ SUNG KHAI BÁO ĐƯỜNG DẪN CHO AUDIT LOGS
    { 
        path: '/audit-logs', 
        name: 'AuditLogs', 
        component: AuditLogs 
    },
    {
        path: '/users',
        name: 'UserManager',
        component: UserManager
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation Guard (Giữ lại logic bảo vệ route và mở rộng thêm)
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('access_token')
    
    
    // Danh sách các trang cần phải đăng nhập mới được vào
    const protectedRoutes = ['/dashboard', '/audit-logs', '/users']
    
    // Nếu vào trang cần bảo vệ mà không có token -> Đuổi về trang login
    if (protectedRoutes.includes(to.path) && !token) {
        next('/login')
    } 
    // Nếu đã đăng nhập rồi mà cố tình vào lại trang login -> Đẩy vào dashboard
    else if (to.path === '/login' && token) {
        next('/dashboard')
    } 
    // Các trường hợp hợp lệ khác cho qua bình thường
    else {
        next()
    }
})

// --- QUAN TRỌNG NHẤT LÀ DÒNG NÀY ---
export default router