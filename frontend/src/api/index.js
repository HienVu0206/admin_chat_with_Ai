import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

// ==========================================
// 1. CẤU HÌNH AXIOS (Dành cho các file cũ)
// ==========================================
export const api = axios.create({
    baseURL: API_BASE_URL, 
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor (Giữ nguyên logic của mày)
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});


// ==========================================
// 2. HÀM TIỆN ÍCH ĐĂNG XUẤT 
// ==========================================
export const forceLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
};


// ==========================================
// 3. HÀM FETCH TỰ ĐỘNG REFRESH TOKEN (Dành cho Dashboard)
// ==========================================
export const fetchWithAuth = async (url, options = {}) => {
    let token = localStorage.getItem('access_token');
    
    // Gắn token vào header
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    // Gọi API lần 1
    let response = await fetch(url, { ...options, headers });

    // Nếu Backend báo 401 (Token hết hạn)
    if (response.status === 401) {
        console.log("Access Token hết hạn! Đang thử dùng Refresh Token...");
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (refreshToken) {
            try {
                // Nhớ đổi '/admin/refresh' thành API thực tế của mày nếu backend quy định khác nhé
                const refreshRes = await fetch(`${API_BASE_URL}/admin/refresh`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: refreshToken }) 
                });

                if (refreshRes.ok) {
                    const data = await refreshRes.json();
                    
                    // Lưu token mới vào LocalStorage
                    localStorage.setItem('access_token', data.access_token);
                    if (data.refresh_token) {
                        localStorage.setItem('refresh_token', data.refresh_token);
                    }
                    
                    // Gọi lại cái API ban đầu bị xịt với token mới
                    headers['Authorization'] = `Bearer ${data.access_token}`;
                    response = await fetch(url, { ...options, headers });
                } else {
                    throw new Error("Refresh token cũng tèo rồi!");
                }
            } catch (error) {
                console.error("Lỗi refresh token, buộc đăng xuất:", error);
                forceLogout();
            }
        } else {
            // Không có refresh token luôn thì cook
            forceLogout();
        }
    }

    return response;
};