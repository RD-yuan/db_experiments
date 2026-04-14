<template>
  <div class="admin-layout">
    <el-container>
      <el-aside width="220px">
        <div class="brand">后台管理</div>
        <el-menu :default-active="$route.path" router>
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataLine /></el-icon>
            <span>数据看板</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/products">
            <el-icon><Goods /></el-icon>
            <span>商品管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/orders">
            <el-icon><Document /></el-icon>
            <span>订单管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/coupons">
            <el-icon><Ticket /></el-icon>
            <span>优惠券管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="topbar">
          <div class="topbar-title">管理后台</div>
          <div class="topbar-actions">
            <span class="admin-name">{{ userStore.user?.username || '管理员' }}</span>
            <el-button text @click="router.push('/home')">返回前台</el-button>
            <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
          </div>
        </el-header>

        <el-main class="content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const handleLogout = async () => {
  await userStore.logout()
  ElMessage.success('已退出登录')
  router.replace('/login')
}
</script>

<style lang="scss" scoped>
.admin-layout {
  min-height: 100vh;
}

.brand {
  padding: 20px 16px;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.el-aside {
  background: #001529;
}

.el-aside :deep(.el-menu) {
  border-right: none;
  background: transparent;
}

.el-aside :deep(.el-menu-item) {
  color: #dbeafe;
}

.el-aside :deep(.el-menu-item:hover) {
  background: #0f2747;
}

.el-aside :deep(.el-menu-item.is-active) {
  background: #ff6700;
  color: #fff;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}

.topbar-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-name {
  color: #606266;
}

.content {
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>
