<template>
  <div class="auth-page auth-register">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Register</h1>
        <p>Create an account and sign in immediately.</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" class="auth-form register-form" label-position="top">
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" size="large" placeholder="Choose a username" />
        </el-form-item>

        <el-form-item label="Phone" prop="phone">
          <el-input v-model="form.phone" size="large" placeholder="Optional" />
        </el-form-item>

        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" size="large" placeholder="Optional" />
        </el-form-item>

        <el-form-item label="Password" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            size="large"
            show-password
            placeholder="Create a password"
          />
        </el-form-item>

        <el-form-item label="Confirm password" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            size="large"
            show-password
            placeholder="Enter the password again"
            @keyup.enter="handleRegister"
          />
        </el-form-item>

        <el-button class="submit-button" type="primary" size="large" :loading="loading" @click="handleRegister">
          Register
        </el-button>
      </el-form>

      <div class="auth-footer">
        <span>Already have an account?</span>
        <router-link to="/login">Log in</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { sessionApi } from '@/api/session-api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const form = reactive({
  username: '',
  phone: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('Please confirm your password'))
    return
  }

  if (value !== form.password) {
    callback(new Error('The two passwords do not match'))
    return
  }

  callback()
}

const rules = {
  username: [
    { required: true, message: 'Please enter a username', trigger: 'blur' },
    { min: 2, max: 20, message: 'Username length must be between 2 and 20', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^$|^1[3-9]\d{9}$/, message: 'Please enter a valid phone number', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter a password', trigger: 'blur' },
    { min: 6, max: 20, message: 'Password length must be between 6 and 20', trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!formRef.value) {
    return
  }

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) {
    return
  }

  loading.value = true

  try {
    const data = await sessionApi.auth.register({
      username: form.username.trim(),
      phone: form.phone.trim() || undefined,
      email: form.email.trim() || undefined,
      password: form.password
    })

    userStore.setAuth(data)
    ElMessage.success('Registration successful')
    router.replace('/')
  } catch (error) {
    const message = error?.response?.data?.message || error?.message || 'Registration failed'
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

.auth-register {
  background: linear-gradient(135deg, #99f6e4 0%, #14b8a6 45%, #0f766e 100%);
}

.auth-card {
  width: 100%;
  max-width: 460px;
  padding: 36px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 24px 60px rgba(15, 118, 110, 0.18);
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
  color: #0f766e;
}
</style>
