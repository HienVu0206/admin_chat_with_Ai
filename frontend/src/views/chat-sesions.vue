<template>
  <div class="chat-sessions-container">
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
          <h1>Danh sách đoạn chát</h1>
          <p class="header-subtitle">Xem lịch sử tất cả các đoạn hội thoại</p>
        </div>
      </div>
      <div class="header-stats">
        <span class="stat-badge">{{ sessions.length }} đoạn chát</span>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="search-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <input v-model="searchQuery" type="text" placeholder="Tìm kiếm theo tên, tiêu đề..." class="search-input"/>
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

    <!-- Sessions Table -->
    <div class="table-wrapper">
      <table class="sessions-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Tên người dùng</th>
            <th>Tiêu đề đoạn chát</th>
            <th>Ngày tạo</th>
            <th>Cập nhật lần cuối</th>
            <th>Trạng thái</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="session in filteredSessions" :key="session.id" class="session-row">
            <td class="session-id">{{ session.id }}</td>
            <td class="user-name">
              <div class="user-avatar">{{ session.userName.charAt(0) }}</div>
              <span>{{ session.userName }}</span>
            </td>
            <td class="session-title">
              <div class="title-text">{{ session.title }}</div>
              <div class="message-count">{{ session.messageCount }} tin nhắn</div>
            </td>
            <td class="created-date">{{ formatDate(session.createdAt) }}</td>
            <td class="updated-date">{{ formatDate(session.updatedAt) }}</td>
            <td class="status-cell">
              <span :class="['status-badge', `status-${session.status}`]">
                {{ session.status === 'active' ? 'Hoạt động' : 'Đã kết thúc' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="filteredSessions.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <p>Không tìm thấy đoạn chát nào</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface ChatSession {
  id: number;
  userName: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
  status: 'active' | 'ended';
}

const searchQuery = ref('');
const sortBy = ref('recent');

const sessions = ref<ChatSession[]>([
  {
    id: 1,
    userName: 'Nguyễn Văn A',
    title: 'Hướng dẫn học Vue.js',
    createdAt: new Date('2024-03-10'),
    updatedAt: new Date('2024-03-15'),
    messageCount: 45,
    status: 'active',
  },
  {
    id: 2,
    userName: 'Trần Thị B',
    title: 'Tư vấn lập trình web',
    createdAt: new Date('2024-03-08'),
    updatedAt: new Date('2024-03-14'),
    messageCount: 28,
    status: 'active',
  },
  {
    id: 3,
    userName: 'Lê Minh C',
    title: 'Cấu trúc dữ liệu và giải thuật',
    createdAt: new Date('2024-03-05'),
    updatedAt: new Date('2024-03-12'),
    messageCount: 62,
    status: 'ended',
  },
  {
    id: 4,
    userName: 'Phạm Hữu D',
    title: 'Thiết kế database',
    createdAt: new Date('2024-03-02'),
    updatedAt: new Date('2024-03-10'),
    messageCount: 35,
    status: 'active',
  },
  {
    id: 5,
    userName: 'Hoàng Thu E',
    title: 'Xây dựng REST API',
    createdAt: new Date('2024-02-28'),
    updatedAt: new Date('2024-03-08'),
    messageCount: 51,
    status: 'ended',
  },
  {
    id: 6,
    userName: 'Đặng Quý F',
    title: 'Tối ưu hóa hiệu suất ứng dụng',
    createdAt: new Date('2024-02-25'),
    updatedAt: new Date('2024-03-05'),
    messageCount: 39,
    status: 'active',
  },
]);

const filteredSessions = computed(() => {
  let result = sessions.value;

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(
      session =>
        session.userName.toLowerCase().includes(query) ||
        session.title.toLowerCase().includes(query)
    );
  }

  // Sort
  if (sortBy.value === 'recent') {
    result.sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
  } else if (sortBy.value === 'oldest') {
    result.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());
  } else if (sortBy.value === 'name') {
    result.sort((a, b) => a.userName.localeCompare(b.userName));
  } else if (sortBy.value === 'title') {
    result.sort((a, b) => a.title.localeCompare(b.title));
  }

  return result;
});

const formatDate = (date: Date) => {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  };
  return new Date(date).toLocaleDateString('vi-VN', options);
};

const goBack = () => {
  window.history.back();
};
</script>
