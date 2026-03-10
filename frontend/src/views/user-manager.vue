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
        <input 
          v-model="searchQuery" 
          @input="debouncedSearch" 
          type="text" 
          placeholder="Tìm kiếm người dùng theo tên hoặc email..." 
          class="search-input" 
        />
      </div>
      <div class="filters">
        <select v-model="filterRoleId" @change="fetchUsers" class="filter-select">
          <option :value="null">Tất cả quyền hạn</option>
          <option v-for="role in rolesList" :key="role.id" :value="role.id">
            {{ role.name }}
          </option>
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
          <tr v-if="users.length === 0">
            <td colspan="5" style="text-align: center; padding: 30px; color: #666;">
              Không tìm thấy người dùng nào.
            </td>
          </tr>
          <tr v-for="user in users" :key="user.id">
            <td>#{{ user.id }}</td>
            <td class="user-info">
              <div class="user-name">{{ user.full_name }}</div>
              <div class="user-email">{{ user.email }}</div>
            </td>
            
            <td class="status-cell">
              <span :class="['badge', user.status === 'active' ? 'badge-active' : 'badge-banned']">
                {{ user.status === 'active' ? 'Hoạt động' : 'Bị khóa' }}
              </span>
            </td>

            <td class="role-cell">
              <select 
                :value="user.role_id" 
                @change="onRoleChange(user, $event)" 
                class="role-select"
                :disabled="user.status !== 'active'" 
              >
                <option v-for="role in rolesList" :key="role.id" :value="role.id">
                  {{ role.name }}
                </option>
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
        <h3>Xác nhận hành động</h3>
        <p>{{ confirmDialog.message }}</p>
        
        <div v-if="confirmDialog.action === 'ban'" class="reason-input-wrapper">
          <label style="display: block; margin-top: 15px; font-size: 14px; font-weight: 500;">
            Lý do khóa:
          </label>
          <input 
            v-model="confirmDialog.reason" 
            type="text" 
            placeholder="Nhập lý do khóa tài khoản..." 
            class="search-input" 
            style="width: 100%; margin-top: 5px; box-sizing: border-box;" 
          />
        </div>

        <div class="modal-actions">
          <button @click="closeConfirm" class="btn btn-cancel">Hủy</button>
          <button 
            @click="submitChange" 
            class="btn btn-confirm"
            :disabled="confirmDialog.action === 'ban' && !confirmDialog.reason.trim()"
          >
            Đồng ý
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

// Cấu hình URL Backend (sử dụng biến môi trường hoặc fallback về localhost)
// @ts-ignore
const API_BASE_URL = import.meta.env?.VITE_API_URL || 'http://127.0.0.1:8000';

// Khai báo Interface
interface User {
  id: number;
  full_name: string;
  email: string;
  created_at: string;
  status: string;     
  role_id: number;    
}

interface Role { 
  id: number; 
  name: string; 
}

// Khai báo State
const users = ref<User[]>([]);
const rolesList = ref<Role[]>([]);
const searchQuery = ref('');
const filterRoleId = ref<number | null>(null);

const confirmDialog = ref({ 
  show: false, 
  action: '', 
  data: null as any, 
  message: '',
  reason: '' 
});

// Hàm lấy Headers cho Axios (đính kèm Token)
const getHeaders = () => {
  const token = localStorage.getItem('access_token');
  return { 
    headers: { Authorization: `Bearer ${token}` } 
  };
};

// Hàm gọi API lấy danh sách người dùng
const fetchUsers = async () => {
  try {
    const params: any = {};
    if (searchQuery.value) params.search = searchQuery.value;
    if (filterRoleId.value) params.role_id = filterRoleId.value;
    
    const res = await axios.get(`${API_BASE_URL}/admin/users`, { ...getHeaders(), params });
    users.value = res.data;
  } catch (e) { 
    console.error('Lỗi khi tải danh sách người dùng:', e); 
  }
};

// Hàm gọi API lấy danh sách Role
const fetchRoles = async () => {
    try {
        const res = await axios.get(`${API_BASE_URL}/admin/roles`, getHeaders());
        rolesList.value = res.data;
    } catch (e) { 
        console.error('Lỗi khi tải danh sách quyền:', e); 
    }
};

// Xử lý khi Admin chọn đổi Role từ Dropdown
const onRoleChange = (user: User, event: Event) => {
  const newRoleId = Number((event.target as HTMLSelectElement).value);
  if (newRoleId === user.role_id) return;
  
  // Trả select về giá trị cũ tạm thời trong lúc chờ xác nhận
  (event.target as HTMLSelectElement).value = String(user.role_id); 

  const roleName = rolesList.value.find(r => r.id === newRoleId)?.name || newRoleId;

  confirmDialog.value = {
    show: true,
    action: 'change_role',
    data: { userId: user.id, newRoleId },
    message: `Bạn có chắc chắn muốn đổi quyền của người dùng "${user.full_name}" thành "${roleName}"?`,
    reason: ''
  };
};

// Xử lý khi Admin bấm nút Khóa / Mở khóa
const openConfirm = (user: User, type: 'ban' | 'unban') => {
  confirmDialog.value = {
    show: true,
    action: type,
    data: { userId: user.id },
    message: `Bạn có chắc muốn ${type === 'ban' ? 'KHÓA' : 'MỞ KHÓA'} tài khoản "${user.full_name}"?`,
    reason: ''
  };
};

const closeConfirm = () => {
  confirmDialog.value.show = false;
  confirmDialog.value.reason = ''; // Reset lý do
};

// Thực thi hành động sau khi xác nhận trên Modal
const submitChange = async () => {
  const { action, data, reason } = confirmDialog.value;
  closeConfirm();

  try {
    if (action === 'change_role') {
      await axios.put(
        `${API_BASE_URL}/admin/users/${data.userId}/role`, 
        { new_role_id: data.newRoleId }, 
        getHeaders()
      );
    } 
    else if (action === 'ban') {
      await axios.patch(
        `${API_BASE_URL}/admin/users/${data.userId}/ban`,
        { reason: reason }, // Body theo schema BanUserRequest
        getHeaders()
      );
    }
    else if (action === 'unban') {
      await axios.patch(
        `${API_BASE_URL}/admin/users/${data.userId}/unban`,
        null,
        getHeaders()
      );
    }
    
    // Tải lại danh sách sau khi thay đổi thành công
    await fetchUsers(); 
    alert("Thao tác thành công!");
  } catch (error: any) {
    console.error(error);
    const msg = error.response?.data?.detail || "Đã xảy ra lỗi từ máy chủ API";
    alert("Lỗi: " + (typeof msg === 'string' ? msg : JSON.stringify(msg)));
  }
};

// Debounce chức năng tìm kiếm (tránh gọi API liên tục khi gõ)
let timeout: ReturnType<typeof setTimeout>;
const debouncedSearch = () => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    fetchUsers();
  }, 500);
};

// Hook chạy ngay khi Component được Mount
onMounted(() => {
  fetchRoles();
  fetchUsers();
});

// Chức năng nút quay lại
const goBack = () => window.history.back();
</script>

<style scoped>
/* Reset & Container */
.user-management-container { 
  padding: 24px; 
  background: #f8f9fa; 
  min-height: 100vh; 
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
}

/* Header */
.page-header { 
  background: white; 
  padding: 20px 24px; 
  border-radius: 12px; 
  margin-bottom: 24px; 
  box-shadow: 0 1px 3px rgba(0,0,0,0.05); 
}
.header-content { display: flex; flex-direction: column; gap: 8px; }
.header-title h1 { margin: 0; font-size: 24px; color: #111827; }
.back-btn { 
  align-self: flex-start;
  padding: 8px 16px; 
  border: 1px solid #e5e7eb; 
  background: white; 
  color: #374151;
  border-radius: 6px; 
  cursor: pointer; 
  font-weight: 500;
  transition: all 0.2s ease;
}
.back-btn:hover { background: #f9fafb; border-color: #d1d5db; }

/* Toolbar (Search & Filter) */
.toolbar { display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.search-wrapper { flex: 1; min-width: 250px; }
.search-input { 
  width: 100%; 
  padding: 10px 14px; 
  border: 1px solid #e5e7eb; 
  border-radius: 8px; 
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}
.search-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }
.filter-select { 
  padding: 10px 14px; 
  border: 1px solid #e5e7eb; 
  border-radius: 8px; 
  font-size: 14px;
  background-color: white;
  outline: none;
  cursor: pointer;
}

/* Table */
.table-wrapper { 
  background: white; 
  border-radius: 12px; 
  overflow-x: auto; 
  box-shadow: 0 1px 3px rgba(0,0,0,0.05); 
}
.users-table { width: 100%; border-collapse: collapse; white-space: nowrap; }
.users-table th, .users-table td { padding: 16px 24px; text-align: left; border-bottom: 1px solid #f3f4f6; }
.users-table th { 
  background: #f9fafb; 
  font-weight: 600; 
  color: #6b7280; 
  font-size: 12px; 
  text-transform: uppercase; 
  letter-spacing: 0.05em;
}

/* User Info */
.user-info { display: flex; flex-direction: column; gap: 4px; }
.user-name { font-weight: 500; color: #111827; }
.user-email { font-size: 13px; color: #6b7280; }

/* Badges */
.badge { padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 600; display: inline-block; }
.badge-active { background: #d1fae5; color: #047857; }
.badge-banned { background: #fee2e2; color: #b91c1c; }

/* Role Select in Table */
.role-select { 
  padding: 6px 12px; 
  border-radius: 6px; 
  border: 1px solid #e5e7eb; 
  background: white;
  font-size: 14px;
  cursor: pointer;
}
.role-select:disabled { background: #f3f4f6; cursor: not-allowed; }

/* Action Buttons */
.actions-cell { display: flex; gap: 8px; }
.btn-action { 
  padding: 6px 14px; 
  border-radius: 6px; 
  border: 1px solid transparent; 
  cursor: pointer; 
  font-size: 13px; 
  font-weight: 500; 
  transition: all 0.2s;
}
.btn-ban { background: #fff1f2; border-color: #fecdd3; color: #e11d48; }
.btn-ban:hover { background: #ffe4e6; }
.btn-unban { background: #ecfdf5; border-color: #a7f3d0; color: #059669; }
.btn-unban:hover { background: #d1fae5; }

/* Modal */
.modal-overlay { 
  position: fixed; 
  inset: 0; 
  background: rgba(17, 24, 39, 0.6); 
  backdrop-filter: blur(2px);
  display: flex; 
  align-items: center; 
  justify-content: center; 
  z-index: 999; 
}
.modal-content { 
  background: white; 
  padding: 24px; 
  border-radius: 12px; 
  width: 400px; 
  max-width: 90%; 
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
.modal-content h3 { margin-top: 0; margin-bottom: 12px; font-size: 18px; color: #111827; }
.modal-content p { color: #4b5563; font-size: 14px; line-height: 1.5; margin-bottom: 0; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-confirm { 
  background: #2563eb; 
  color: white; 
  border: none; 
  padding: 8px 16px; 
  border-radius: 6px; 
  cursor: pointer; 
  font-weight: 500;
}
.btn-confirm:hover:not(:disabled) { background: #1d4ed8; }
.btn-confirm:disabled { background: #93c5fd; cursor: not-allowed; }
.btn-cancel { 
  background: #f3f4f6; 
  color: #374151; 
  border: 1px solid #e5e7eb; 
  padding: 8px 16px; 
  border-radius: 6px; 
  cursor: pointer; 
  font-weight: 500;
}
.btn-cancel:hover { background: #e5e7eb; }
</style>