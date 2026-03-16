<template>
  <div class="chat-sessions-container">
    <div class="page-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Quay lại
        </button>
        <div class="header-title">
          <h1>Danh sách đoạn chát</h1>
          <p class="header-subtitle">Xem lịch sử tất cả các đoạn hội thoại</p>
        </div>
      </div>
      <div class="header-stats">
        <span class="stat-badge">{{ sessions.length }} đoạn chát</span>
      </div>
    </div>

    <div class="toolbar">
      <div class="search-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <input 
          v-model="searchQuery" 
          @input="debounceSearch" 
          type="text" 
          placeholder="Tìm kiếm theo tên, tiêu đề..." 
          class="search-input"
        />
      </div>
      
      <div class="sort-wrapper">
        <select v-model="sortBy" class="sort-select">
          <option value="recent">Mới nhất</option>
          <option value="oldest">Cũ nhất</option>
          <option value="name">Tên người dùng</option>
          <option value="title">Tiêu đề</option>
        </select>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state" style="text-align: center; padding: 3rem; color: #666;">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="animation: spin 1s linear infinite;">
        <line x1="12" y1="2" x2="12" y2="6"></line>
        <line x1="12" y1="18" x2="12" y2="22"></line>
        <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
        <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
        <line x1="2" y1="12" x2="6" y2="12"></line>
        <line x1="18" y1="12" x2="22" y2="12"></line>
        <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
        <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
      </svg>
      <p style="margin-top: 10px;">Đang tải dữ liệu từ server...</p>
    </div>

    <div v-else class="table-wrapper">
      <table class="sessions-table">
        <thead>
          <tr>
            <!-- <th>ID</th> -->
            <th>Tên người dùng</th>
            <th>Tiêu đề đoạn chát</th>
            <th>Ngày tạo</th>
            <th>Cập nhật lần cuối</th>
            <!-- <th>Trạng thái</th> -->
          </tr>
        </thead>
        <tbody>
          <tr v-for="session in paginatedSessions" :key="session.id" class="session-row">
            <!-- <td class="session-id">{{ session.id }}</td> -->
            <td class="user-name">
              <div class="user-avatar">{{ session.user_name ? session.user_name.charAt(0).toUpperCase() : '?' }}</div>
              <span>{{ session.user_name || 'Khách' }}</span>
            </td>
            <td class="session-title">
              <div class="title-text">{{ session.title || 'Chưa có tiêu đề' }}</div>
            </td>
            <td class="created-date">{{ formatDate(session.created_at) }}</td>
            <td class="updated-date">{{ formatDate(session.updated_at) }}</td>
            <!-- <td class="status-cell">
              <span class="status-badge status-active">
                Hoạt động
              </span>
            </td> -->
          </tr>
        </tbody>
      </table>
      
      <div v-if="filteredSessions.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <p>Không tìm thấy đoạn chát nào</p>
      </div>

      <div v-if="filteredSessions.length > 0" class="pagination-wrapper">
        <div class="pagination-info">
          Hiển thị {{ startIndex + 1 }} - {{ Math.min(endIndex, filteredSessions.length) }} trong tổng số {{ filteredSessions.length }} đoạn chat
        </div>
        <div class="pagination-controls">
          <button class="page-btn" :disabled="currentPage === 1" @click="prevPage">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <path d="M15 18l-6-6 6-6"/>
            </svg>
            Trước
          </button>
          
          <div class="page-numbers">
            <span class="current-page">Trang {{ currentPage }} / {{ totalPages }}</span>
          </div>

          <button class="page-btn" :disabled="currentPage === totalPages || totalPages === 0" @click="nextPage">
            Sau
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';

interface ChatSession {
  id: number;
  user_name: string | null;
  title: string | null;
  created_at: string;
  updated_at: string;
}

const searchQuery = ref('');
const sortBy = ref('recent');
const sessions = ref<ChatSession[]>([]);
const isLoading = ref(true);

// --- STATE QUẢN LÝ PHÂN TRANG ---
const itemsPerPage = 10;
const currentPage = ref(1);

const fetchConversations = async (search = '') => {
  isLoading.value = true;
  try {
    const token = localStorage.getItem('access_token'); 
    
    const response = await axios.get(`http://localhost:8000/admin/conversations`, { 
      params: { search: search },
      headers: { Authorization: `Bearer ${token}` }
    });
    
    sessions.value = response.data;
  } catch (error) {
    console.error("Lỗi khi tải danh sách đoạn chat:", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchConversations();
});

let searchTimeout: ReturnType<typeof setTimeout>;
const debounceSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchConversations(searchQuery.value);
  }, 500); 
};

// Sắp xếp dữ liệu
const filteredSessions = computed(() => {
  let result = [...sessions.value];

  if (sortBy.value === 'recent') {
    result.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
  } else if (sortBy.value === 'oldest') {
    result.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
  } else if (sortBy.value === 'name') {
    result.sort((a, b) => (a.user_name || '').localeCompare(b.user_name || ''));
  } else if (sortBy.value === 'title') {
    result.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
  }

  return result;
});

// --- LOGIC PHÂN TRANG ---
watch([searchQuery, sortBy], () => {
  currentPage.value = 1; // Đổi sort hay search thì quay về trang 1
});

const totalPages = computed(() => Math.ceil(filteredSessions.value.length / itemsPerPage) || 1);
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => startIndex.value + itemsPerPage);

const paginatedSessions = computed(() => {
  return filteredSessions.value.slice(startIndex.value, endIndex.value);
});

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++;
};
// -----------------------

const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  };
  return new Date(dateString).toLocaleDateString('vi-VN', options);
};

const goBack = () => {
  window.history.back();
};
</script>

<style scoped>
@import '../assets/css/chat-sesions.css';

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* CSS CHO THANH PHÂN TRANG */
.pagination-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  background-color: #f8fafc;
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
}

.pagination-info {
  font-size: 0.875rem;
  color: #64748b;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #3b82f6;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #eff6ff;
  border-color: #bfdbfe;
}

.page-btn:disabled {
  color: #94a3b8;
  background-color: #f1f5f9;
  cursor: not-allowed;
}

.current-page {
  font-size: 0.875rem;
  font-weight: 500;
  color: #334155;
}
</style>