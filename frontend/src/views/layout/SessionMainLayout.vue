<template>
  <div class="layout-shell">
    <header class="topbar">
      <router-link class="brand" to="/home">Ecommerce Platform</router-link>

      <nav class="nav-links">
        <router-link to="/home">Home</router-link>
        <router-link to="/products">Products</router-link>
        <router-link to="/cart">Cart</router-link>
        <router-link to="/orders">Orders</router-link>
      </nav>

      <div v-if="userStore.isLoggedIn" class="account-actions">
        <span class="welcome-text">{{ displayName }}</span>
        <el-button text @click="router.push('/user/profile')">Profile</el-button>
        <el-button type="danger" plain size="small" @click="handleLogout">Logout</el-button>
      </div>

      <div v-else class="guest-actions">
        <router-link to="/login">Login</router-link>
        <router-link to="/register">Register</router-link>
      </div>
    </header>

    <main class="page-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const displayName = computed(() => {
  return userStore.user?.username || userStore.user?.phone || userStore.user?.email || 'Signed in user'
})

const handleLogout = async () => {
  await userStore.logout()
  ElMessage.success('Logged out')
  router.replace('/login')
}
</script>

<style lang="scss" scoped>
.layout-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 0 24px;
  min-height: 64px;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.brand {
  font-size: 20px;
  font-weight: 700;
  color: #ea580c;
}

.nav-links,
.guest-actions,
.account-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-links {
  flex: 1;
}

.welcome-text {
  color: #4b5563;
  font-size: 14px;
}

.topbar a {
  color: #111827;
}

.topbar a.router-link-active,
.topbar a:hover {
  color: #ea580c;
}

.page-content {
  flex: 1;
}
</style>
