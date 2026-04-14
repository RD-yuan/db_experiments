<template>
  <div class="auth-page auth-login">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Login</h1>
        <p>Sign in with your account to continue.</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" class="auth-form login-form" label-position="top">
        <el-form-item label="Username / Phone / Email" prop="username">
          <el-input
            v-model="form.username"
            size="large"
            placeholder="Enter your account"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item label="Password" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            size="large"
            show-password
            placeholder="Enter your password"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-button class="submit-button" type="primary" size="large" :loading="loading" @click="handleLogin">
          Login
        </el-button>
      </el-form>

      <div class="auth-footer">
        <span>No account yet?</span>
        <router-link to="/register">Create one</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { sessionApi } from '@/api/session-api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: 'Please enter your account', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) {
    return
  }

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) {
    return
  }

  loading.value = true

  try {
    const data = await sessionApi.auth.login({
      username: form.username.trim(),
      password: form.password
    })

    userStore.setAuth(data)
    ElMessage.success('Login successful')
    router.replace(typeof route.query.redirect === 'string' ? route.query.redirect : '/')
  } catch (error) {
    const message = error?.response?.data?.message || error?.message || 'Login failed'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.auth-login {
  background: linear-gradient(135deg, #fed7aa 0%, #fb923c 45%, #ea580c 100%);
}

.auth-card {
  width: 100%;
  max-width: 440px;
  padding: 36px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 24px 60px rgba(124, 45, 18, 0.18);
}

.auth-header {
  margin-bottom: 24px;
}

.auth-header h1 {
  margin: 0 0 8px;
  color: #111827;
  font-size: 32px;
}

.auth-header p {
  margin: 0;
  color: #6b7280;
}

.submit-button {
  width: 100%;
}

.auth-footer {
  margin-top: 20px;
  color: #6b7280;
  text-align: center;
}

.auth-footer a {
  margin-left: 6px;
  color: #c2410c;
}
</style>
