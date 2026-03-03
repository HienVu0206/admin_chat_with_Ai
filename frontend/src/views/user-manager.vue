<template>
  <div class="user-management-container">
    <div class="page-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">Quay lại</button>
        <div class="header-title">
          <h1>Quản lý Người dùng</h1>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <div class="search-wrapper">
        <input v-model="searchQuery" @input="debouncedSearch" type="text" placeholder="Tìm kiếm..." class="search-input" />
      </div>
      <div class="filters">
        <select v-model="filterRoleId" @change="fetchUsers" class="filter-select">
          <option :value="null">Tất cả quyền hạn</option>
          <option v-for="role in rolesList" :key="role.id" :value="role.id">{{ role.name }}</option>
        </select>
      </div>
    </div>

    <div class="table-wrapper">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Người dùng</th>
            <th>Trạng thái</th>
            <th>Quyền hạn</th>
            <th>Hành động</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>#{{ user.id }}</td>
            <td class="user-info">
              <div class="user-name">{{ user.full_name }}</div>
              <div class="user-email">{{ user.email }}</div>
            </td>
            
            <td class="status-cell">
              <span :class="['badge', user.status === 'active' ? 'badge-active' : 'badge-banned']">
                {{ user.status === 'active' ? 'Active' : 'Banned' }}
              </span>
            </td>

            <td class="role-cell">
              <select 
                :value="user.role_id" 
                @change="onRoleChange(user, $event)" 
                class="role-select"
                :disabled="user.status !== 'active'" 
              >
                <option v-for="role in rolesList" :key="role.id" :value="role.id">{{ role.name }}</option>
              </select>
            </td>

            <td class="actions-cell">
              <button 
                v-if="user.status === 'active'" 
                class="btn-action btn-ban" 
                @click="openConfirm(user, 'ban')"
              >
                Khóa
              </button>
              <button 
                v-else 
                class="btn-action btn-unban" 
                @click="openConfirm(user, 'unban')"
              >
                Mở khóa
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="confirmDialog.show" class="modal-overlay">
      <div class="modal-content">
        <h3>Xác nhận</h3>
        <p>{{ confirmDialog.message }}</p>
        <div class="modal-actions">
          <button @click="confirmDialog.show = false" class="btn btn-cancel">Hủy</button>
          <button @click="submitChange" class="btn btn-confirm">Đồng ý</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

// @ts-ignore
const API_BASE_URL = import.meta.env?.VITE_API_URL || 'http://127.0.0.1:8000';

// Interface khớp 100% với Database của bạn
interface User {
  id: number;
  full_name: string;
  email: string;
  created_at: string;
  status: string;     // 'active' hoặc 'banned'
  role_id: number;    // ID dạng số (1, 2, 3...)
}

interface Role { id: number; name: string; }

const users = ref<User[]>([]);
const rolesList = ref<Role[]>([]);
const searchQuery = ref('');
const filterRoleId = ref<number | null>(null);
const confirmDialog = ref({ show: false, action: '', data: null as any, message: '' });

const getHeaders = () => {
  const token = localStorage.getItem('access_token');
  return { headers: { Authorization: `Bearer ${token}` } };
};

const fetchUsers = async () => {
  try {
    const params: any = {};
    if (searchQuery.value) params.search = searchQuery.value;
    if (filterRoleId.value) params.role_id = filterRoleId.value;
    
    const res = await axios.get(`${API_BASE_URL}/admin/users`, { ...getHeaders(), params });
    users.value = res.data;
  } catch (e) { console.error(e); }
};

const fetchRoles = async () => {
    try {
        const res = await axios.get(`${API_BASE_URL}/admin/roles`, getHeaders());
        rolesList.value = res.data;
    } catch (e) { console.error(e); }
};

// --- LOGIC XỬ LÝ ---

const onRoleChange = (user: User, event: Event) => {
  const newRoleId = Number((event.target as HTMLSelectElement).value);
  if (newRoleId === user.role_id) return;
  (event.target as HTMLSelectElement).value = String(user.role_id); // Reset UI chờ confirm

  // Tìm tên role để hiển thị thông báo cho đẹp
  const roleName = rolesList.value.find(r => r.id === newRoleId)?.name || newRoleId;

  confirmDialog.value = {
    show: true,
    action: 'change_role',
    data: { userId: user.id, newRoleId },
    message: `Bạn muốn đổi quyền của "${user.full_name}" thành "${roleName}"?`
  };
};

const openConfirm = (user: User, type: 'ban' | 'unban') => {
  confirmDialog.value = {
    show: true,
    action: type,
    data: { userId: user.id },
    message: `Bạn có chắc muốn ${type === 'ban' ? 'KHÓA' : 'MỞ KHÓA'} tài khoản "${user.full_name}"?`
  };
};

const submitChange = async () => {
  const { action, data } = confirmDialog.value;
  confirmDialog.value.show = false;

  try {
    if (action === 'change_role') {
      // FIXED: Gửi JSON Body chuẩn theo Swagger
      // URL: PUT /admin/users/{id}/role
      // Body: { "new_role_id": 1 }
      await axios.put(
        `${API_BASE_URL}/admin/users/${data.userId}/role`, 
        { new_role_id: data.newRoleId }, 
        getHeaders()
      );
    } 
    else if (action === 'ban' || action === 'unban') {
      // FIXED: Gọi API update status mới thêm ở Python
      const newStatus = action === 'ban' ? 'banned' : 'active';
      await axios.put(
        `${API_BASE_URL}/admin/users/${data.userId}/status`,
        { status: newStatus },
        getHeaders()
      );
    }
    
    await fetchUsers(); // Tải lại danh sách
    alert("Thành công!");
  } catch (error: any) {
    console.error(error);
    const msg = error.response?.data?.detail || "Lỗi API";
    alert("Lỗi: " + JSON.stringify(msg));
  }
};

// Debounce Search
let timeout: any;
const debouncedSearch = () => {
  clearTimeout(timeout);
  timeout = setTimeout(fetchUsers, 500);
};

onMounted(() => {
  fetchRoles();
  fetchUsers();
});

const goBack = () => window.history.back();
</script>

<style scoped>
/* CSS giữ nguyên cho đẹp */
.user-management-container { padding: 24px; background: #f8f9fa; min-height: 100vh; font-family: 'Inter', sans-serif; }
.page-header { background: white; padding: 20px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.back-btn { padding: 8px 12px; border: 1px solid #ddd; background: white; border-radius: 6px; cursor: pointer; margin-bottom: 10px; }
.toolbar { display: flex; gap: 16px; margin-bottom: 20px; }
.search-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 8px; }
.filter-select { padding: 10px; border: 1px solid #ddd; border-radius: 8px; }
.table-wrapper { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.users-table { width: 100%; border-collapse: collapse; }
.users-table th, .users-table td { padding: 16px; text-align: left; border-bottom: 1px solid #eee; }
.users-table th { background: #f9fafb; font-weight: 600; color: #666; font-size: 13px; text-transform: uppercase; }

.badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge-active { background: #d1fae5; color: #047857; }
.badge-banned { background: #fee2e2; color: #b91c1c; }

.role-select { padding: 6px; border-radius: 6px; border: 1px solid #ddd; }
.btn-action { padding: 6px 12px; border-radius: 6px; border: 1px solid; cursor: pointer; font-size: 12px; font-weight: 500; }
.btn-ban { background: #fff1f2; border-color: #fecdd3; color: #e11d48; }
.btn-unban { background: #ecfdf5; border-color: #a7f3d0; color: #059669; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 99; }
.modal-content { background: white; padding: 24px; border-radius: 12px; width: 400px; max-width: 90%; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.btn-confirm { background: #2563eb; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
.btn-cancel { background: #f3f4f6; color: #333; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
</style>