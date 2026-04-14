<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <h1>登录</h1>
        <p>使用现有账号进入系统</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" class="auth-form">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名 / 手机号 / 邮箱"
            size="large"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-button type="primary" size="large" class="submit-button" :loading="loading" @click="handleLogin">
          登录
        </el-button>

        <div class="auth-footer">
          <span>还没有账号？</span>
          <router-link to="/register">立即注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
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
  username: [{ required: true, message: '请输入用户名或手机号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ]
}

const handleLogin = () => {
  if (!formRef.value) {
    return
  }

  formRef.value.validate(async (valid) => {
    if (!valid) {
      return
    }

    loading.value = true

    try {
      const data = await api.auth.login({
        username: form.username,
        password: form.password
      })

      userStore.setAuth(data)
      ElMessage.success('登录成功')
      router.replace(route.query.redirect || '/')
    } catch (error) {
      const msg = error?.response?.data?.message || error?.message || '登录失败'
      ElMessage.error(msg)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f97316 0%, #fb923c 45%, #fed7aa 100%);
}

.auth-card {
  width: 420px;
  padding: 40px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 24px 60px rgba(120, 53, 15, 0.18);
}

.auth-header {
  margin-bottom: 24px;
  text-align: center;
}

.auth-header h1 {
  margin: 0 0 8px;
  color: #1f2937;
  font-size: 30px;
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
  text-align: center;
  color: #6b7280;
}

.auth-footer a {
  margin-left: 6px;
  color: #ea580c;
}
</style>
