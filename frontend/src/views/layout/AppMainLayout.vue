<template>
  <div class="layout">
    <el-header class="header">
      <router-link class="logo" to="/home">电商平台</router-link>

      <nav class="nav">
        <router-link to="/home">首页</router-link>
        <router-link to="/products">全部商品</router-link>
        <router-link to="/cart">
          <el-badge :value="cartCount" :hidden="cartCount === 0">购物车</el-badge>
        </router-link>
        <router-link to="/orders">我的订单</router-link>
      </nav>

      <div v-if="userStore.isLoggedIn" class="user-actions">
        <el-dropdown>
          <span class="user-name">{{ userStore.user?.username || userStore.user?.phone || '已登录用户' }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="router.push('/user/profile')">个人中心</el-dropdown-item>
              <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <div v-else class="auth-links">
        <router-link to="/login">登录</router-link>
        <router-link to="/register">注册</router-link>
      </div>
    </el-header>

    <el-main class="main">
      <router-view />
    </el-main>

    <el-footer class="footer">
      <p>Database course project demo</p>
    </el-footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const cartCount = ref(0)

const handleLogout = async () => {
  await userStore.logout()
  ElMessage.success('已退出登录')
  router.replace('/login')
}
</script>

<style lang="scss" scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 0 32px;
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}

.logo {
  color: #ff6700;
  font-size: 22px;
  font-weight: 700;
}

.nav {
  display: flex;
  align-items: center;
  gap: 24px;
  flex: 1;
}

.nav a,
.auth-links a {
  color: #303133;
}

.nav a.router-link-active,
.auth-links a.router-link-active,
.nav a:hover,
.auth-links a:hover,
.logo:hover,
.user-name:hover {
  color: #ff6700;
}

.auth-links {
  display: flex;
  gap: 16px;
}

.user-name {
  color: #303133;
  cursor: pointer;
}

.main {
  flex: 1;
  background: #f5f7fa;
}

.footer {
  text-align: center;
  color: #909399;
  background: #fff;
  border-top: 1px solid #ebeef5;
}
</style>
