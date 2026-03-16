import { createRouter, createWebHistory } from 'vue-router'

// Dùng ../ để trỏ ra ngoài thư mục router, rồi vào thư mục views
import Login from '../views/Login.vue' 
import Dashboard from '../views/Dashboard.vue'
import AuditLogs from '../views/audit-logs.vue' 
import UserManager from '../views/user-manager.vue'
import RoleManagement from '../views/role-management.vue'

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
    { 
        path: '/audit-logs', 
        name: 'AuditLogs', 
        component: AuditLogs 
    },
    {
        path: '/users',
        name: 'UserManager',
        component: UserManager
    },
    {
        path: '/role-management',
        name: 'RoleManagement',
        component: RoleManagement
    },
    {
        path: '/chat-sesions', // Sửa lại lỗi gõ thiếu chữ 's'
        name: 'ChatSessions',
        // Dùng import động (lazy load) trỏ thẳng tới file, sếp nhớ check lại TÊN FILE cho khớp nhé
        component: () => import('../views/chat-sesions.vue') 
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// --- Navigation Guard (Đã được tối ưu) ---
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('access_token');
    
    // Nếu KHÔNG có token và đang cố vào một trang KHÁC trang login -> Đuổi về login
    if (!token && to.path !== '/login') {
        next('/login');
    } 
    // Nếu ĐÃ CÓ token (đã đăng nhập) mà lại mò ra trang login -> Đẩy vào dashboard
    else if (token && to.path === '/login') {
        next('/dashboard');
    } 
    // Các trường hợp hợp lệ khác -> Cho phép đi tiếp bình thường
    else {
        next();
    }
})

export default router