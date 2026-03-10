<template>
  <div class="role-management-container">
    <!-- Header -->
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

    <!-- Toolbar -->
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

    <!-- Roles Table -->
    <div class="table-wrapper">
      <table class="roles-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Tên quyền hạn</th>
            <th>Mô tả</th>
            <th>Số người dùng</th>
            <th>Ngày tạo</th>
            <th>Hành động</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="role in filteredRoles" :key="role.id" class="role-row">
            <td class="role-id">{{ role.id }}</td>
            <td class="role-name">
              <div class="role-badge" :style="{ backgroundColor: role.color }">{{ role.name }}</div>
            </td>
            <td class="role-description">{{ role.description }}</td>
            <td class="role-users">{{ role.userCount }}</td>
            <td class="role-date">{{ formatDate(role.createdAt) }}</td>
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

    <!-- Add/Edit Form Modal -->
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

          <div class="form-group">
            <label>Màu sắc</label>
            <div class="color-picker">
              <button 
                v-for="color in colors" 
                :key="color" 
                type="button"
                class="color-option"
                :style="{ backgroundColor: color }"
                :class="{ active: formData.color === color }"
                @click="formData.color = color"
              ></button>
            </div>
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

    <!-- Delete Confirmation Modal -->
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
import { ref, computed } from 'vue';

interface Role {
  id: number;
  name: string;
  description: string;
  color: string;
  userCount: number;
  createdAt: string;
}

const searchQuery = ref('');
const isLoading = ref(false);

const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#6366f1'];

const roles = ref<Role[]>([
  {
    id: 1,
    name: 'Admin',
    description: 'Quản trị viên hệ thống - có toàn quyền',
    color: '#ef4444',
    userCount: 3,
    createdAt: '2024-01-15',
  },
  {
    id: 2,
    name: 'User',
    description: 'Người dùng bình thường',
    color: '#3b82f6',
    userCount: 245,
    createdAt: '2024-01-01',
  },
  {
    id: 3,
    name: 'Moderator',
    description: 'Điều phối viên - quản lý nội dung',
    color: '#f59e0b',
    userCount: 8,
    createdAt: '2024-02-01',
  },
]);

const formModal = ref({
  show: false,
  mode: 'add' as 'add' | 'edit',
});

const formData = ref({
  id: 0,
  name: '',
  description: '',
  color: '#3b82f6',
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

const goBack = () => {
  window.history.back();
};

const openAddForm = () => {
  formModal.value.mode = 'add';
  formData.value = {
    id: 0,
    name: '',
    description: '',
    color: '#3b82f6',
  };
  formModal.value.show = true;
};

const openEditForm = (role: Role) => {
  formModal.value.mode = 'edit';
  formData.value = {
    id: role.id,
    name: role.name,
    description: role.description,
    color: role.color,
  };
  formModal.value.show = true;
};

const closeForm = () => {
  formModal.value.show = false;
};

const submitForm = async () => {
  isLoading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    if (formModal.value.mode === 'add') {
      const newRole: Role = {
        id: Math.max(...roles.value.map(r => r.id), 0) + 1,
        name: formData.value.name,
        description: formData.value.description,
        color: formData.value.color,
        userCount: 0,
        createdAt: new Date().toISOString().split('T')[0],
      };
      roles.value.push(newRole);
    } else {
      const role = roles.value.find(r => r.id === formData.value.id);
      if (role) {
        role.name = formData.value.name;
        role.description = formData.value.description;
        role.color = formData.value.color;
      }
    }
    closeForm();
  } catch (error) {
    console.error('Error:', error);
  } finally {
    isLoading.value = false;
  }
};

const openDeleteConfirm = (role: Role) => {
  deleteConfirm.value = {
    show: true,
    roleId: role.id,
    roleName: role.name,
  };
};

const cancelDelete = () => {
  deleteConfirm.value.show = false;
};

const confirmDelete = async () => {
  isLoading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    roles.value = roles.value.filter(r => r.id !== deleteConfirm.value.roleId);
    cancelDelete();
  } catch (error) {
    console.error('Error:', error);
  } finally {
    isLoading.value = false;
  }
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('vi-VN');
};
</script>
