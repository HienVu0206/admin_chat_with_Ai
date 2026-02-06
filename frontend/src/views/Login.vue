<template>
  <div class="admin-login-container">
    <div class="admin-login-card">
      <div class="admin-icon">
        <img 
          src="data:image/png;base64,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"
          alt="App Logo"
        />
      </div>

      <h1 class="admin-title">Admin Portal</h1>
      <p class="admin-subtitle">Quản lý ứng dụng của bạn</p>

      <form @submit.prevent="handleLogin" class="admin-form">
        
        <div v-if="errorMessage" class="error-alert">
          {{ errorMessage }}
        </div>

        <div class="form-group">
          <label>Email</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="1"/>
              <path d="M4 6h16M4 6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2z"/>
              <path d="m22 6-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 6"/>
            </svg>
            <input
              v-model="email"
              type="email"
              placeholder="name@example.com"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label>Mật khẩu</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="••••••••"
              required
            />

            <div class="password-toggle" @click="showPassword = !showPassword">
                <svg v-if="!showPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </div>
          </div>
        </div>

        <div class="form-checkbox">
          <input id="remember" v-model="rememberMe" type="checkbox" />
          <label for="remember">Ghi nhớ đăng nhập</label>
        </div>

        <button type="submit" class="login-button" :disabled="isLoading">
          <span v-if="isLoading">Đang xử lý...</span>
          <span v-else>Đăng nhập</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api' 

const router = useRouter()
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await api.post('/admin/login', {
      email: email.value,
      password: password.value
    })

    const { access_token } = response.data
    localStorage.setItem('access_token', access_token)
    router.push('/dashboard')

  } catch (error) {
    console.error('Login error:', error)
    if (error.response && error.response.data) {
        errorMessage.value = error.response.data.detail || 'Đăng nhập thất bại'
    } else {
        errorMessage.value = 'Lỗi kết nối máy chủ'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped src="../assets/css/login.css"></style>