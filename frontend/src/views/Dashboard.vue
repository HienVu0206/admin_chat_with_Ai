<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Quay lại
        </button>
        <div class="header-title" style="display: flex; align-items: center; justify-content: space-between; gap: 20px; width: 100%;">
          <div>
            <h1>Dashboard Cosmic Chat</h1>
            <p class="header-subtitle">Tổng quan hệ thống</p>
          </div>
          
          <div class="header-actions">
            <router-link to="/users" class="action-btn user-btn">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
              Quản lý Users
            </router-link>

            <router-link to="/audit-logs" class="action-btn audit-btn">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
              Nhật ký hoạt động
            </router-link>
          </div>
          
        </div>
      </div>
      <div class="header-time">{{ currentTime }}</div>
    </div>

    <div v-if="loading" style="text-align: center; padding: 20px; color: #666;">
        Đang tải dữ liệu...
    </div>

    <div v-else class="stats-grid">
      
      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-icon-wrapper users-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
          <div class="stat-change positive">
             +{{ stats.new_users_today }} mới
          </div>
        </div>
        <div class="stat-details">
          <div class="stat-value">{{ formatNumber(stats.total_users) }}</div>
          <div class="stat-label">Tổng người dùng</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-icon-wrapper active-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
            </svg>
          </div>
          <div class="stat-change positive">24h qua</div>
        </div>
        <div class="stat-details">
          <div class="stat-value">{{ formatNumber(stats.active_users_24h) }}</div>
          <div class="stat-label">User hoạt động</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-icon-wrapper chats-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
            </svg>
          </div>
          <div class="stat-change positive">Hôm nay</div>
        </div>
        <div class="stat-details">
          <div class="stat-value">{{ formatNumber(stats.new_conversations_today) }}</div>
          <div class="stat-label">Đoạn chat mới</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-icon-wrapper messages-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 6h-2v9H6v2c0 .55.45 1 1 1h11l4 4V7c0-.55-.45-1-1-1zm-4 6V3c0-.55-.45-1-1-1H3c-.55 0-1 .45-1 1v14l4-4h10c.55 0 1-.45 1-1z"/>
            </svg>
          </div>
          <div class="stat-change neutral">Total</div>
        </div>
        <div class="stat-details">
          <div class="stat-value">{{ formatNumber(stats.total_messages) }}</div>
          <div class="stat-label">Tổng tin nhắn</div>
        </div>
      </div>

    </div>

    <div v-if="!loading" class="charts-section">
      
      <div class="chart-card">
        <div class="chart-header">
          <h3>Thống kê Tin nhắn</h3>
          <p class="chart-subtitle">7 ngày gần nhất (User + AI)</p>
        </div>
        <div class="chart-container">
            <div class="chart-bars">
              <div 
                v-for="(item, index) in chartItems" 
                :key="index" 
                class="chart-column"
              >
                <div 
                  class="chart-bar" 
                  :class="{ active: index === chartItems.length - 1 }"
                  :style="{ height: item.heightPercent + '%' }" 
                  :data-value="formatNumber(item.total)"
                  :title="`${item.fullDate}: ${item.total} tin nhắn`"
                ></div>
                <span class="chart-label">{{ item.dayLabel }}</span>
              </div>
            </div>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>Tỷ lệ tin nhắn</h3>
          <p class="chart-subtitle">Phân chia theo nguồn gửi (7 ngày qua)</p>
        </div>
        
        <div class="message-distribution">
          <div class="message-row">
             <div class="msg-info">
                <span class="msg-type">User</span>
                <span class="msg-count">{{ formatNumber(msgDist.userTotal) }}</span>
             </div>
             <div class="progress-bg">
                <div class="progress-fill user-fill" :style="{ width: msgDist.userPercent + '%' }"></div>
             </div>
             <div class="msg-percent">{{ msgDist.userPercent }}%</div>
          </div>

          <div class="message-row">
            <div class="msg-info">
               <span class="msg-type">AI Bot</span>
               <span class="msg-count">{{ formatNumber(msgDist.aiTotal) }}</span>
            </div>
            <div class="progress-bg">
               <div class="progress-fill ai-fill" :style="{ width: msgDist.aiPercent + '%' }"></div>
            </div>
            <div class="msg-percent">{{ msgDist.aiPercent }}%</div>
         </div>
        </div>

        <div class="message-total-footer">
            Tổng cộng 7 ngày: <strong>{{ formatNumber(msgDist.totalPeriod) }} tin nhắn</strong>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// @ts-ignore
const API_BASE_URL = import.meta.env?.VITE_API_URL || 'http://127.0.0.1:8000'; 

const loading = ref(true);
const currentTime = ref('');

const stats = ref({
  total_users: 0,
  new_users_today: 0,
  active_users_24h: 0,
  total_messages: 0,
  new_conversations_today: 0,
  total_posts: 0,
  pending_reports: 0
});

const chartItems = ref([]);
const msgDist = ref({
  userTotal: 0,
  userPercent: 0,
  aiTotal: 0,
  aiPercent: 0,
  totalPeriod: 0
});

const goBack = () => {
  window.history.back();
};

const formatNumber = (num) => {
  return new Intl.NumberFormat('en-US').format(num);
};

const getDayLabel = (dateStr) => {
  const date = new Date(dateStr);
  const days = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
  return days[date.getDay()];
};

const fetchData = async () => {
  try {
    loading.value = true;

    const token = localStorage.getItem('access_token'); 
    
    const config = {
      headers: { Authorization: `Bearer ${token}` }
    };

   const [summaryRes, chartRes] = await Promise.all([
     axios.get(`${API_BASE_URL}/dashboard/summary`, config), 
     axios.get(`${API_BASE_URL}/dashboard/charts/messages?days=7`, config)
   ]);

    stats.value = summaryRes.data;
    const rawChartData = chartRes.data;

    let maxVal = 0;
    let sumUser = 0;
    let sumAI = 0;

    const processedData = rawChartData.map(item => {
      const total = item.user_count + item.ai_count;
      if (total > maxVal) maxVal = total;
      
      sumUser += item.user_count;
      sumAI += item.ai_count;

      return {
        dayLabel: getDayLabel(item.date),
        fullDate: item.date,
        total: total,
        user: item.user_count,
        ai: item.ai_count,
        heightPercent: 0 
      };
    });

    chartItems.value = processedData.map(item => ({
      ...item,
      heightPercent: maxVal > 0 ? (item.total / maxVal) * 100 : 0
    }));

    const totalPeriod = sumUser + sumAI;
    msgDist.value = {
      userTotal: sumUser,
      aiTotal: sumAI,
      totalPeriod: totalPeriod,
      userPercent: totalPeriod > 0 ? Math.round((sumUser / totalPeriod) * 100) : 0,
      aiPercent: totalPeriod > 0 ? Math.round((sumAI / totalPeriod) * 100) : 0,
    };

 } catch (error) {
    console.error("Lỗi khi tải dữ liệu dashboard:", error);
    if (error.response && error.response.status === 401) {
       alert("Phiên đăng nhập đã hết hạn hoặc bạn không có quyền. Vui lòng đăng nhập lại!");
       localStorage.removeItem('access_token');
       window.location.href = '/login'; 
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  const updateTime = () => {
    const now = new Date();
    const options = {
      weekday: 'long',
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    try {
        currentTime.value = now.toLocaleDateString('vi-VN', options);
    } catch (e) {
        currentTime.value = now.toLocaleString();
    }
  };
  
  updateTime();
  setInterval(updateTime, 60000);

  fetchData();
});
</script>

<style scoped src="../assets/css/dashboard.css"></style>

<style scoped>
/* CSS cho nhóm nút điều hướng */
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

/* Nút Nhật ký hoạt động (Màu xanh dương) */
.audit-btn {
  background-color: #e0e7ff;
  color: #4f46e5;
}
.audit-btn:hover {
  background-color: #4f46e5;
  color: #ffffff;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
}

/* Nút Quản lý Users (Màu xanh lá) */
.user-btn {
  background-color: #dcfce7;
  color: #16a34a;
}
.user-btn:hover {
  background-color: #16a34a;
  color: #ffffff;
  box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.2);
}
</style>