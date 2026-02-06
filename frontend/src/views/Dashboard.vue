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
        <div class="header-title">
          <h1>Dashboard Cosmic Chat</h1>
          <p class="header-subtitle">Tổng quan hệ thống</p>
        </div>
      </div>
      <div class="header-time">{{ currentTime }}</div>
    </div>

    <div v-if="loading" style="text-align: center; padding: 20px; color: #fff;">
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

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

// --- Cấu hình API URL ---
// Nếu Backend chạy port 8000, Frontend port khác, cần set full URL hoặc config Proxy
const API_BASE_URL = 'http://127.0.0.1:8000'; 

// --- Interfaces cho dữ liệu ---
interface DashboardSummary {
  total_users: number;
  new_users_today: number;
  active_users_24h: number;
  total_messages: number;
  new_conversations_today: number;
  total_posts: number;
  pending_reports: number;
}

interface MessageChartPoint {
  date: string;
  user_count: number;
  ai_count: number;
}

interface ChartItemDisplay {
  dayLabel: string;   // T2, T3...
  fullDate: string;   // 2023-10-20
  total: number;      // user + ai
  heightPercent: number; // Để vẽ CSS height
}

// --- State ---
const loading = ref(true);
const currentTime = ref('');

// Giá trị mặc định ban đầu
const stats = ref<DashboardSummary>({
  total_users: 0,
  new_users_today: 0,
  active_users_24h: 0,
  total_messages: 0,
  new_conversations_today: 0,
  total_posts: 0,
  pending_reports: 0
});

const chartItems = ref<ChartItemDisplay[]>([]);
const msgDist = ref({
  userTotal: 0,
  userPercent: 0,
  aiTotal: 0,
  aiPercent: 0,
  totalPeriod: 0
});

// --- Functions ---

const goBack = () => {
  window.history.back();
};

const formatNumber = (num: number) => {
  return new Intl.NumberFormat('en-US').format(num);
};

// Hàm lấy ngày trong tuần (CN, T2, T3...)
const getDayLabel = (dateStr: string) => {
  const date = new Date(dateStr);
  const days = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
  return days[date.getDay()];
};

// --- Fetch Data ---
const fetchData = async () => {
  try {
    loading.value = true;

    // 1. Gọi API Summary
    const summaryRes = await axios.get(`${API_BASE_URL}/dashboard/summary`);
    stats.value = summaryRes.data;

    // 2. Gọi API Charts (7 ngày)
    const chartRes = await axios.get(`${API_BASE_URL}/dashboard/charts/messages?days=7`);
    const rawChartData: MessageChartPoint[] = chartRes.data;

    // --- Xử lý dữ liệu cho Biểu đồ Cột ---
    // Tìm giá trị lớn nhất để tính % chiều cao
    let maxVal = 0;
    const processedData = rawChartData.map(item => {
      const total = item.user_count + item.ai_count;
      if (total > maxVal) maxVal = total;
      return {
        dayLabel: getDayLabel(item.date),
        fullDate: item.date,
        total: total,
        user: item.user_count,
        ai: item.ai_count,
        heightPercent: 0 // Tính sau
      };
    });

    // Tính % height (nếu max = 0 thì set 0 để tránh chia cho 0)
    chartItems.value = processedData.map(item => ({
      ...item,
      heightPercent: maxVal > 0 ? (item.total / maxVal) * 100 : 0
    }));

    // --- Xử lý dữ liệu cho Thanh Phân Bố (Distribution) ---
    // Cộng dồn 7 ngày qua
    let sumUser = 0;
    let sumAI = 0;
    processedData.forEach(item => {
      sumUser += item.user;
      sumAI += item.ai;
    });
    
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
    // Có thể thêm thông báo lỗi UI ở đây
  } finally {
    loading.value = false;
  }
};

// --- Lifecycle ---
onMounted(() => {
  // Cập nhật đồng hồ
  const updateTime = () => {
    const now = new Date();
    const options: Intl.DateTimeFormatOptions = {
      weekday: 'long',
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    // Fix lỗi hiển thị tiếng Việt trên một số trình duyệt
    try {
        currentTime.value = now.toLocaleDateString('vi-VN', options);
    } catch (e) {
        currentTime.value = now.toLocaleString();
    }
  };
  
  updateTime();
  setInterval(updateTime, 60000);

  // Gọi API lấy dữ liệu
  fetchData();
});
</script>

<style scoped src="../assets/css/dashboard.css"></style>