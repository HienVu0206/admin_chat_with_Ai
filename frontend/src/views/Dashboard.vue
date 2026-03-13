<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Quay lại
        </button>
        <div class="header-title-wrapper">
          <div>
            <h1>Dashboard Cosmic Chat</h1>
            <p class="header-subtitle">Tổng quan hệ thống</p>
          </div>

          <div class="header-actions-wrapper">
            <button class="mobile-menu-btn" @click="isMenuOpen = !isMenuOpen">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
                <circle cx="12" cy="5" r="2"></circle>
                <circle cx="12" cy="12" r="2"></circle>
                <circle cx="12" cy="19" r="2"></circle>
              </svg>
            </button>

            <div class="header-actions" :class="{ 'is-open': isMenuOpen }">
              <router-link to="/role-management" class="action-btn role-btn" @click="isMenuOpen = false">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
                Quản lý Quyền
              </router-link>

              <router-link to="/users" class="action-btn user-btn" @click="isMenuOpen = false">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
                Quản lý Users
              </router-link>

              <router-link to="/audit-logs" class="action-btn audit-btn" @click="isMenuOpen = false">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                Nhật ký
              </router-link>

              <button @click="handleLogout" class="action-btn logout-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                  <polyline points="16 17 21 12 16 7"></polyline>
                  <line x1="21" y1="12" x2="9" y2="12"></line>
                </svg>
                Đăng xuất
              </button>
            </div>
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
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
            </svg>
          </div>
          <div class="stat-change positive">+{{ stats.new_users_today }} mới</div>
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
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
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
              <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" />
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
              <path d="M21 6h-2v9H6v2c0 .55.45 1 1 1h11l4 4V7c0-.55-.45-1-1-1zm-4 6V3c0-.55-.45-1-1-1H3c-.55 0-1 .45-1 1v14l4-4h10c.55 0 1-.45 1-1z" />
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
            <div v-for="(item, index) in chartItems" :key="index" class="chart-column">
              <div class="chart-bar" :class="{ active: index === chartItems.length - 1 }"
                :style="{ height: item.heightPercent + '%' }" :data-value="formatNumber(item.total)"
                :title="`${item.fullDate}: ${item.total} tin nhắn`"></div>
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
import { useRouter } from 'vue-router'; 
// Import hàm fetchWithAuth để xử lý việc tự động refresh token
import { fetchWithAuth } from '../api/index.js'; 

// @ts-ignore
const API_BASE_URL = import.meta.env?.VITE_API_URL || 'http://127.0.0.1:8000';

const router = useRouter(); 
const loading = ref(true);
const currentTime = ref('');
const isMenuOpen = ref(false); 

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
const msgDist = ref({ userTotal: 0, userPercent: 0, aiTotal: 0, aiPercent: 0, totalPeriod: 0 });

const goBack = () => { window.history.back(); };

const handleLogout = () => {
  if (confirm("Bạn có chắc chắn muốn đăng xuất khỏi hệ thống?")) {
    // Phải xóa cả 2 token nhé
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    router.push('/login');
  }
};

const formatNumber = (num) => { return new Intl.NumberFormat('en-US').format(num || 0); };

const getDayLabel = (dateStr) => {
  const date = new Date(dateStr);
  const days = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
  return days[date.getDay()];
};

const fetchData = async () => {
  try {
    loading.value = true;
    
    // Gọi API thông qua hàm fetchWithAuth để tận dụng tính năng tự refresh token
    const [summaryRes, chartRes] = await Promise.all([
      fetchWithAuth(`${API_BASE_URL}/dashboard/summary`),
      fetchWithAuth(`${API_BASE_URL}/dashboard/charts/messages?days=7`)
    ]);

    if (!summaryRes.ok || !chartRes.ok) {
        throw new Error("Không thể tải dữ liệu.");
    }

    const summaryData = await summaryRes.json();
    const rawChartData = await chartRes.json();

    stats.value = summaryData;

    let maxVal = 0, sumUser = 0, sumAI = 0;

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
    console.error("Lỗi khi tải Dashboard:", error);
    // Lưu ý: Việc redirect về /login khi hết hạn token đã được hàm fetchWithAuth tự lo rồi
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  const updateTime = () => {
    const now = new Date();
    currentTime.value = now.toLocaleDateString('vi-VN', {
      weekday: 'long', year: 'numeric', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  };
  updateTime();
  setInterval(updateTime, 60000);
  fetchData();
});
</script>

<style scoped src="../assets/css/dashboard.css"></style>