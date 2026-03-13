<template>
  <div class="role-management-container">
    <div class="page-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Quay lại
        </button>
        <div class="header-title">
          <h1>Quản lý Quyền hạn (Role)</h1>
          <p class="header-subtitle">Tạo, chỉnh sửa và xóa các quyền hạn trong hệ thống</p>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <div class="search-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <input v-model="searchQuery" type="text" placeholder="Tìm kiếm quyền hạn..." class="search-input"/>
      </div>
      <button class="btn btn-primary" @click="openAddForm">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 5v14M5 12h14"/>
        </svg>
        Thêm quyền hạn
      </button>
    </div>

    <div class="table-wrapper">
      <table class="roles-table">
        <thead>
          <tr>
            <th>Tên quyền hạn</th>
            <th>Mô tả</th>
            <th>Hành động</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="role in filteredRoles" :key="role.id" class="role-row">
            <td class="role-name">
              <div class="role-badge" :style="{ backgroundColor: role.color }">{{ role.name }}</div>
            </td>
            <td class="role-description">{{ role.description }}</td>
            <td class="actions-cell">
              <div class="action-buttons">
                <button class="btn-action btn-edit" @click="openEditForm(role)" title="Chỉnh sửa">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z"/>
                    <path d="m20.71-8.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                  </svg>
                  Sửa
                </button>
                <button class="btn-action btn-delete" @click="openDeleteConfirm(role)" title="Xóa" v-if="role.id > 2">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-9l-1 1H5v2h14V4z"/>
                  </svg>
                  Xóa
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="formModal.show" class="modal-overlay" @click.self="closeForm">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ formModal.mode === 'add' ? 'Thêm quyền hạn mới' : 'Chỉnh sửa quyền hạn' }}</h3>
          <button class="close-btn" @click="closeForm">×</button>
        </div>

        <form @submit.prevent="submitForm" class="role-form">
          <div class="form-group">
            <label>Tên quyền hạn</label>
            <input v-model="formData.name" type="text" placeholder="VD: Moderator" required class="form-input"/>
          </div>

          <div class="form-group">
            <label>Mô tả</label>
            <textarea v-model="formData.description" placeholder="Mô tả về quyền hạn..." class="form-textarea"></textarea>
          </div>

          <div class="form-actions">
            <button type="button" class="btn btn-cancel" @click="closeForm">Hủy</button>
            <button type="submit" class="btn btn-confirm" :disabled="isLoading">
              {{ isLoading ? 'Đang xử lý...' : (formModal.mode === 'add' ? 'Thêm' : 'Cập nhật') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="deleteConfirm.show" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal-content">
        <h3>Xác nhận xóa quyền hạn</h3>
        <p>Bạn có chắc chắn muốn xóa quyền hạn <strong>{{ deleteConfirm.roleName }}</strong>? Hành động này không thể hoàn tác.</p>
        <div class="modal-actions">
          <button class="btn btn-cancel" @click="cancelDelete">Hủy</button>
          <button class="btn btn-confirm btn-danger" @click="confirmDelete" :disabled="isLoading">
            {{ isLoading ? 'Đang xử lý...' : 'Xóa' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

interface Role {
  id: number;
  name: string;
  description: string;
  color: string;
  userCount: number;
  createdAt: string;
}

const API_BASE_URL = 'http://localhost:8000/admin';

const searchQuery = ref('');
const isLoading = ref(false);
const roles = ref<Role[]>([]); 

//lấy màu ở đây
const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#6366f1'];

const formModal = ref({
  show: false,
  mode: 'add' as 'add' | 'edit',
});

const formData = ref({
  id: 0,
  name: '',
  description: '',
});

const deleteConfirm = ref({
  show: false,
  roleId: 0,
  roleName: '',
});

const filteredRoles = computed(() => {
  return roles.value.filter(role =>
    role.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    role.description.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
};

const fetchRoles = async () => {
  try {
    isLoading.value = true;
    const response = await fetch(`${API_BASE_URL}/roles`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) throw new Error('Không thể tải danh sách quyền hạn');
    const data = await response.json();
    
    roles.value = data.map((item: any, index: number) => ({
      id: item.id,
      name: item.name || 'Không có tên',
      description: item.description || '',
      color: colors[index % colors.length], 
      userCount: 0, 
      createdAt: new Date().toISOString() 
    }));
    
  } catch (error) {
    console.error('Lỗi khi fetch roles:', error);
  } finally {
    isLoading.value = false;
  }
};

const submitForm = async () => {
  isLoading.value = true;
  try {
    const payload = {
      name: formData.value.name,
      description: formData.value.description,
    };

    if (formModal.value.mode === 'add') {
      const response = await fetch(`${API_BASE_URL}/roles`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error('Lỗi khi thêm quyền hạn');
    } else {
      const response = await fetch(`${API_BASE_URL}/roles/${formData.value.id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error('Lỗi khi cập nhật quyền hạn');
    }
    
    closeForm();
    await fetchRoles(); 

  } catch (error) {
    console.error('Error:', error);
    alert('Có lỗi xảy ra, vui lòng thử lại!');
  } finally {
    isLoading.value = false;
  }
};

const confirmDelete = async () => {
  isLoading.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/roles/${deleteConfirm.value.roleId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) throw new Error('Lỗi khi xóa quyền hạn');
    
    roles.value = roles.value.filter(r => r.id !== deleteConfirm.value.roleId);
    cancelDelete();
    
  } catch (error) {
    console.error('Error:', error);
    alert('Không thể xóa quyền hạn này!');
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchRoles();
});

const goBack = () => {
  window.history.back();
};

const openAddForm = () => {
  formModal.value.mode = 'add';
  formData.value = { id: 0, name: '', description: '' };
  formModal.value.show = true;
};

const openEditForm = (role: Role) => {
  formModal.value.mode = 'edit';
  formData.value = { id: role.id, name: role.name, description: role.description };
  formModal.value.show = true;
};

const closeForm = () => {
  formModal.value.show = false;
};

const openDeleteConfirm = (role: Role) => {
  deleteConfirm.value = { show: true, roleId: role.id, roleName: role.name };
};

const cancelDelete = () => {
  deleteConfirm.value.show = false;
};

const formatDate = (date: string) => {
  if (!date) return '';
  return new Date(date).toLocaleDateString('vi-VN');
};
</script>

<style scoped src="../assets/css/role-management.css"></style>