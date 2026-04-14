<template>
  <div class="admin-shell">
    <aside class="sidebar">
      <div class="sidebar-title">Admin Console</div>

      <nav class="sidebar-links">
        <router-link to="/admin/dashboard">Dashboard</router-link>
        <router-link to="/admin/users">Users</router-link>
        <router-link to="/admin/products">Products</router-link>
        <router-link to="/admin/orders">Orders</router-link>
        <router-link to="/admin/coupons">Coupons</router-link>
      </nav>
    </aside>

    <section class="admin-main">
      <header class="admin-topbar">
        <div>
          <div class="admin-heading">Admin Console</div>
          <div class="admin-subtitle">{{ displayName }}</div>
        </div>

        <div class="admin-actions">
          <el-button text @click="router.push('/home')">Back to site</el-button>
          <el-button type="danger" plain @click="handleLogout">Logout</el-button>
        </div>
      </header>

      <main class="admin-content">
        <router-view />
      </main>
    </section>
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
  return userStore.user?.username || userStore.user?.phone || 'Admin'
})

const handleLogout = async () => {
  await userStore.logout()
  ElMessage.success('Logged out')
  router.replace('/login')
}
</script>

<style lang="scss" scoped>
.admin-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 220px 1fr;
  background: #f3f4f6;
}

.sidebar {
  background: #111827;
  color: #f9fafb;
  padding: 24px 16px;
}

.sidebar-title {
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 700;
}

.sidebar-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar-links a {
  padding: 10px 12px;
  border-radius: 8px;
  color: #d1d5db;
}

.sidebar-links a.router-link-active,
.sidebar-links a:hover {
  background: #ea580c;
  color: #ffffff;
}

.admin-main {
  display: flex;
  flex-direction: column;
}

.admin-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.admin-heading {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
}

.admin-subtitle {
  margin-top: 4px;
  color: #6b7280;
  font-size: 14px;
}

.admin-actions {
  display: flex;
  gap: 12px;
}

.admin-content {
  flex: 1;
  padding: 24px;
}
</style>
