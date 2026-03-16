<template>
  <div class="audit-logs-container">
    <div class="page-header">
      <div class="header-left">
        <button class="btn-back" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          <span class="back-text">Quay lại</span>
        </button>
        <div class="title-group">
          <h1 class="page-title">Nhật ký hoạt động</h1>
          <p class="page-subtitle">Theo dõi các thao tác của quản trị viên hệ thống</p>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="state-card loading">
      <div class="spinner"></div>
      <p>Đang tải dữ liệu hệ thống...</p>
    </div>
    
    <div v-else-if="error" class="state-card error">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
      <p>{{ error }}</p>
    </div>

    <div v-else class="content-card">
      <div class="table-responsive">
        <table class="audit-table">
          <thead>
            <tr>
              <th width="15%">THỜI GIAN</th>
              <th width="20%">QUẢN TRỊ VIÊN</th>
              <th width="20%">HÀNH ĐỘNG</th>
              <th width="15%">ĐỐI TƯỢNG</th>
              <th width="30%">CHI TIẾT</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="currentPageLogs.length === 0">
              <td colspan="5" class="empty-state">Không có lịch sử hoạt động nào được ghi nhận.</td>
            </tr>
            
            <tr v-for="log in currentPageLogs" :key="log.id">
              <td class="cell-time">{{ formatDateTime(log.created_at) }}</td>
              <td class="cell-admin">
                <div class="admin-badge">
                  <div class="admin-avatar">{{ log.admin_name.charAt(0).toUpperCase() }}</div>
                  <span>{{ log.admin_name }}</span>
                </div>
              </td>
              <td class="cell-action">
                <span :class="['status-pill', `action-${log.action}`]">
                  {{ getActionLabel(log.action) }}
                </span>
              </td>
              <td class="cell-target">{{ log.target_id ? `#${log.target_id}` : '--' }}</td>
              <td class="cell-details">{{ log.details || 'Không có mô tả chi tiết' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="pagination-wrapper" v-if="totalPages > 1">
      <button class="btn-page" :disabled="currentPage === 1" @click="currentPage--">
        ← Trang trước
      </button>
      <div class="page-indicator">
        Trang <strong>{{ currentPage }}</strong> / {{ totalPages }}
      </div>
      <button class="btn-page" :disabled="currentPage === totalPages" @click="currentPage++">
        Trang sau →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
// Import fetchWithAuth để đồng bộ cơ chế Refresh Token
import { fetchWithAuth } from '../api/index.js';

// Đồng bộ URL với Dashboard
// @ts-ignore
const API_BASE_URL = import.meta.env?.VITE_API_URL || 'http://127.0.0.1:8000';

interface AuditLog {
  id: number;
  admin_name: string;
  action: string;
  target_id: number | null;
  details: string | null;
  created_at: string;
}

const logs = ref<AuditLog[]>([]);
const isLoading = ref(false);
const error = ref('');
const currentPage = ref(1);
const itemsPerPage = 10; 

const fetchAuditLogs = async () => {
  isLoading.value = true;
  error.value = '';
  
  try {
    // Gọi API qua fetchWithAuth để lỡ token hết hạn nó tự xin lại
    const response = await fetchWithAuth(`${API_BASE_URL}/admin/audit-logs?limit=100`, {
      method: 'GET'
    });

    // Lúc này lỗi 401 đã được fetchWithAuth lo, mình chỉ bắt lỗi 403 (cấm truy cập) và các lỗi khác
    if (response.status === 403) {
      throw new Error('Bạn không có quyền xem nhật ký hệ thống.');
    }

    if (!response.ok) throw new Error('Không thể tải dữ liệu từ máy chủ.');

    const data = await response.json();
    logs.value = data; 
  } catch (err: any) {
    error.value = err.message || 'Lỗi kết nối máy chủ.';
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchAuditLogs();
});

const totalPages = computed(() => Math.ceil(logs.value.length / itemsPerPage) || 1);

const currentPageLogs = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  return logs.value.slice(startIndex, startIndex + itemsPerPage);
});

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleString('vi-VN', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  });
};

const getActionLabel = (action: string) => {
  const labels: Record<string, string> = {
    'CHANGE_ROLE': 'Đổi quyền', 'BAN_USER': 'Cấm người dùng',
    'UNBAN_USER': 'Gỡ cấm', 'DELETE_POST': 'Xóa bài viết',
    'RESOLVE_REPORT': 'Giải quyết báo cáo', 'DELETE_COMMENT': 'Xóa bình luận',
  };
  return labels[action] || action;
};

const goBack = () => window.history.back();
</script>

<style scoped src="../assets/css/audit-logs.css"></style>