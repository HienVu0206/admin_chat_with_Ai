<template>
  <div class="user-management-container">
    <div class="page-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Quay lại
        </button>
        <div class="header-title">
          <h1>Quản lý Người dùng</h1>
          <p class="header-subtitle">Cấp quyền và quản lý tài khoản</p>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <div class="search-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <input v-model="searchQuery" type="text" placeholder="Tìm kiếm theo Email hoặc Tên..." class="search-input"/>
      </div>
      
      <div class="filters">
        <select v-model="filterStatus" class="filter-select">
          <option value="">Tất cả trạng thái</option>
          <option value="active">Active</option>
          <option value="banned">Banned</option>
        </select>
        
        <select v-model="filterRole" class="filter-select">
          <option value="">Tất cả quyền hạn</option>
          <option v-for="role in rolesList" :key="role.id" :value="role.name">
            {{ formatRoleName(role.name) }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="isFetching" style="text-align: center; padding: 20px; color: #666;">
      Đang tải dữ liệu người dùng...
    </div>

    <div v-else class="table-wrapper">
      <table class="users-table">
        <thead>
          <tr>
            
            <th>Người dùng</th>
            <th>Ngày tham gia</th>
            <th>Trạng thái</th>
            <th>Quyền hạn</th>
            <th>Hành động</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredUsers.length === 0">
            <td colspan="6" style="text-align: center; padding: 20px;">Không tìm thấy người dùng nào.</td>
          </tr>
          
          <tr v-for="user in filteredUsers" :key="user.id" class="user-row">
            <!-- <td class="user-id">{{ user.id }}</td> -->
            <td class="user-info">
              <div class="user-avatar">{{ user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U' }}</div>
              <div class="user-details">
                <div class="user-name">{{ user.full_name }}</div>
                <div class="user-email">{{ user.email }}</div>
              </div>
            </td>
            <td class="join-date">{{ formatDate(user.created_at) }}</td>
            <td class="status-cell">
              <span :class="['badge', `badge-${user.status}`]">
                {{ user.status === 'active' ? 'Active' : 'Banned' }}
              </span>
            </td>
            <td class="role-cell">
              <select 
                :value="user.role" 
                @change="onRoleChange(user, $event)" 
                class="role-select" 
                :disabled="user.status === 'banned'"
              >
                <option v-for="role in rolesList" :key="role.id" :value="role.name">
                  {{ formatRoleName(role.name) }}
                </option>
              </select>
            </td>
            <td class="actions-cell">
              <div class="action-buttons">
                <button 
                  v-if="user.status === 'active'" 
                  class="btn-action btn-ban" 
                  @click="openBanConfirm(user)"
                  title="Khóa tài khoản"
                >
                  <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
                  </svg>
                  Khóa
                </button>
                <button 
                  v-else 
                  class="btn-action btn-unban" 
                  @click="openUnbanConfirm(user)"
                  title="Mở khóa tài khoản"
                >
                  <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                  Mở khóa
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="confirmDialog.show" class="modal-overlay" @click.self="cancelChange">
      <div class="modal-content">
        <template v-if="confirmDialog.action === 'role'">
          <h3>Xác nhận thay đổi quyền hạn</h3>
          <p>Bạn có chắc chắn muốn đổi quyền của <strong>{{ confirmDialog.userName }}</strong> thành <strong>{{ formatRoleName(confirmDialog.newRole) }}</strong> không?</p>
        </template>
        <template v-else-if="confirmDialog.action === 'ban'">
          <h3>Khóa tài khoản người dùng</h3>
          <p>Bạn có chắc chắn muốn khóa tài khoản <strong>{{ confirmDialog.userName }}</strong>? Người dùng này sẽ không thể đăng nhập.</p>
        </template>
        <template v-else-if="confirmDialog.action === 'unban'">
          <h3>Mở khóa tài khoản người dùng</h3>
          <p>Bạn có chắc chắn muốn mở khóa tài khoản <strong>{{ confirmDialog.userName }}</strong>?</p>
        </template>
        
        <div class="modal-actions">
          <button class="btn btn-cancel" @click="cancelChange">Hủy</button>
          <button 
            class="btn btn-confirm" 
            :class="{ 'btn-danger': confirmDialog.action === 'ban' }" 
            @click="confirmChange" 
            :disabled="isLoading"
          >
            {{ isLoading ? 'Đang xử lý...' : 'Đồng ý' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

// Bịt mắt trình duyệt lỗi của VS Code bằng dòng @ts-ignore bên dưới
// @ts-ignore
const API_BASE_URL = import.meta.env?.VITE_API_URL || 'http://127.0.0.1:8000';

// Cập nhật Interface User
interface User {
  id: number;
  full_name: string;
  email: string;
  created_at: string;
  status: 'active' | 'banned';
  role: string; // Chuyển sang string thay vì fix cứng 'user' | 'admin'
}

// Thêm Interface cho Role
interface Role {
  id: number;
  name: string;
  description?: string;
}

const searchQuery = ref('');
const filterStatus = ref('');
const filterRole = ref('');
const isLoading = ref(false);
const isFetching = ref(false);

const users = ref<User[]>([]);
const rolesList = ref<Role[]>([]); // Biến lưu danh sách Role từ API

const confirmDialog = ref({
  show: false,
  userId: 0,
  userName: '',
  newRole: '',
  action: '' as 'role' | 'ban' | 'unban',
});

// Helper lấy Token
const getAuthConfig = () => {
  const token = localStorage.getItem('access_token');
  return {
    headers: { Authorization: `Bearer ${token}` }
  };
};

// Xử lý lỗi chung
const handleApiError = (error: any) => {
  console.error('API Error:', error);
  if (error.response && error.response.status === 401) {
    alert("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!");
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  } else {
    alert(error.response?.data?.detail || "Đã xảy ra lỗi. Vui lòng thử lại!");
  }
};

// API 1: Lấy danh sách Roles
const fetchRoles = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/admin/roles`, getAuthConfig());
    rolesList.value = response.data;
  } catch (error) {
    console.error("Lỗi khi tải danh sách roles:", error);
  }
};

// API 2: Lấy danh sách Users
const fetchUsers = async () => {
  isFetching.value = true;
  try {
    const response = await axios.get(`${API_BASE_URL}/admin/users`, getAuthConfig());
    users.value = response.data;
  } catch (error) {
    handleApiError(error);
  } finally {
    isFetching.value = false;
  }
};

// Gọi cả 2 API khi mount
onMounted(() => {
  fetchRoles();
  fetchUsers();
});

// Tiện ích format tên Role (viết hoa chữ cái đầu)
const formatRoleName = (roleName: string) => {
  if (!roleName) return '';
  return roleName.charAt(0).toUpperCase() + roleName.slice(1);
};

// Computed Search & Filter
const filteredUsers = computed(() => {
  return users.value.filter(user => {
    const nameStr = user.full_name ? user.full_name.toLowerCase() : '';
    const emailStr = user.email ? user.email.toLowerCase() : '';
    const searchStr = searchQuery.value.toLowerCase();
    
    const matchesSearch = nameStr.includes(searchStr) || emailStr.includes(searchStr);
    const matchesStatus = !filterStatus.value || user.status === filterStatus.value;
    const matchesRole = !filterRole.value || user.role === filterRole.value;
    
    return matchesSearch && matchesStatus && matchesRole;
  });
});

const formatDate = (dateStr: string) => {
  if (!dateStr) return 'N/A';
  const date = new Date(dateStr);
  return date.toLocaleDateString('vi-VN', { year: 'numeric', month: '2-digit', day: '2-digit' });
};

// Mở Modal Xác Nhận đổi Role
const onRoleChange = (user: User, event: Event) => {
  const newRole = (event.target as HTMLSelectElement).value; // Bỏ ép kiểu hẹp
  if (newRole !== user.role) {
    confirmDialog.value = { show: true, userId: user.id, userName: user.full_name, newRole, action: 'role' };
    (event.target as HTMLSelectElement).value = user.role; // Đặt lại select chờ xác nhận
  }
};

const openBanConfirm = (user: User) => {
  confirmDialog.value = { show: true, userId: user.id, userName: user.full_name, newRole: '', action: 'ban' };
};

const openUnbanConfirm = (user: User) => {
  confirmDialog.value = { show: true, userId: user.id, userName: user.full_name, newRole: '', action: 'unban' };
};

// API: Submit thay đổi
const confirmChange = async () => {
  isLoading.value = true;
  try {
    const userId = confirmDialog.value.userId;
    const config = getAuthConfig();

    if (confirmDialog.value.action === 'role') {
      // Gọi API cập nhật role
      await axios.put(`${API_BASE_URL}/admin/users/${userId}/role`, { role: confirmDialog.value.newRole }, config);
    } 
    else if (confirmDialog.value.action === 'ban') {
      await axios.post(`${API_BASE_URL}/admin/users/${userId}/ban`, {}, config);
    } 
    else if (confirmDialog.value.action === 'unban') {
      await axios.post(`${API_BASE_URL}/admin/users/${userId}/unban`, {}, config);
    }

    await fetchUsers(); 
    cancelChange();
  } catch (error) {
    handleApiError(error);
  } finally {
    isLoading.value = false;
  }
};

const cancelChange = () => {
  confirmDialog.value.show = false;
};

const goBack = () => {
  window.history.back();
};
</script>

<style scoped src="../assets/css/user-manager.css"></style>