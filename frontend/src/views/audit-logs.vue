<template>
  <div class="audit-logs-container">
    <div class="page-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Quay lại
        </button>
        <div class="header-title">
          <h1>Nhật ký hoạt động</h1>
          <p class="header-subtitle">Theo dõi các thao tác của quản trị viên</p>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="status-message">Đang tải dữ liệu...</div>
    <div v-else-if="error" class="status-message error-message">{{ error }}</div>

    <div v-else class="table-wrapper">
      <table class="audit-table">
        <thead>
          <tr>
            <th>Thời gian</th>
            <th>Quản trị viên</th>
            <th>Hành động</th>
            <th>Đối tượng</th>
            <th>Chi tiết</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="currentPageLogs.length === 0">
            <td colspan="5" style="text-align: center; padding: 20px;">Không có nhật ký hoạt động nào.</td>
          </tr>
          
          <tr v-for="log in currentPageLogs" :key="log.id" class="log-row">
            <td class="timestamp">{{ formatDateTime(log.created_at) }}</td>
            <td class="admin-name">{{ log.admin_name }}</td>
            <td class="action-cell">
              <span :class="['badge', `action-${log.action}`]">
                {{ getActionLabel(log.action) }}
              </span>
            </td>
            <td class="target-id">{{ log.target_id || 'N/A' }}</td>
            <td class="details">{{ log.details || 'Không có chi tiết' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination" v-if="totalPages > 1">
      <button 
        :disabled="currentPage === 1" 
        @click="currentPage--"
        class="pagination-btn"
      >
        ← Trang trước
      </button>
      
      <div class="page-info">
        Trang {{ currentPage }} / {{ totalPages }}
      </div>
      
      <button 
        :disabled="currentPage === totalPages" 
        @click="currentPage++"
        class="pagination-btn"
      >
        Trang sau →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

// 1. Cập nhật Interface khớp với Backend Schema (AuditLogResponse)
interface AuditLog {
  id: number;
  admin_name: string;
  action: string;
  target_id: number | null;
  details: string | null;
  created_at: string;
}

// 2. State quản lý UI và dữ liệu
const logs = ref<AuditLog[]>([]);
const isLoading = ref(false);
const error = ref('');

const currentPage = ref(1);
const itemsPerPage = 10; // FE tự phân trang từ mảng trả về

// 3. Hàm gọi API
const fetchAuditLogs = async () => {
  isLoading.value = true;
  error.value = '';
  
  try {
    const token = localStorage.getItem('access_token'); 
    
    const response = await fetch('http://127.0.0.1:8000/admin/audit-logs?limit=100', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

   if (response.status === 401 || response.status === 403) {
      // BỔ SUNG 2 DÒNG NÀY
      localStorage.removeItem('access_token');
      window.location.href = '/login';
      
      throw new Error('Bạn không có quyền truy cập hoặc phiên đăng nhập đã hết hạn.');
    }

    if (!response.ok) {
      throw new Error('Lỗi khi tải dữ liệu từ máy chủ.');
    }

    const data = await response.json();
    logs.value = data; // Gán dữ liệu thật vào state
    
  } catch (err: any) {
    error.value = err.message || 'Đã xảy ra lỗi không xác định.';
    console.error('Fetch Logs Error:', err);
  } finally {
    isLoading.value = false;
  }
};

// Gọi hàm fetch ngay khi component được render
onMounted(() => {
  fetchAuditLogs();
});

// 4. Các Computed & Methods (Đã sửa lại key cho khớp dữ liệu thật)
const totalPages = computed(() => {
  return Math.ceil(logs.value.length / itemsPerPage) || 1;
});

const currentPageLogs = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  return logs.value.slice(startIndex, startIndex + itemsPerPage);
});

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

const getActionLabel = (action: string) => {
  const labels: Record<string, string> = {
    'CHANGE_ROLE': 'Đổi quyền',
    'BAN_USER': 'Cấm người dùng',
    'UNBAN_USER': 'Gỡ cấm',
    'DELETE_POST': 'Xóa bài viết',
    'RESOLVE_REPORT': 'Giải quyết báo cáo',
    'DELETE_COMMENT': 'Xóa bình luận',
  };
  return labels[action] || action;
};

const goBack = () => {
  window.history.back();
};
</script>

<style scoped src="../assets/css/audit-logs.css"></style>

<style scoped>
.status-message {
  text-align: center;
  padding: 40px;
  font-size: 16px;
  color: #666;
}
.error-message {
  color: #dc3545;
}
</style>