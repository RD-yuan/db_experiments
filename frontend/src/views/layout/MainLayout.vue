<template>
  <div class="layout">
    <el-header class="header">
      <div class="logo">电商平台</div>
      <div class="nav">
        <router-link to="/">首页</router-link>
        <router-link to="/products">全部商品</router-link>
        <router-link to="/cart">
          <el-badge :value="cartCount" :hidden="cartCount === 0">
            购物车
          </el-badge>
        </router-link>
        <router-link to="/orders">我的订单</router-link>
      </div>
      <div class="user-info" v-if="isLoggedIn">
        <el-dropdown>
          <span class="user-name">{{ user?.username }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/user/profile')">个人中心</el-dropdown-item>
              <el-dropdown-item @click="handleLogout">退出</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <div v-else class="auth-buttons">
        <router-link to="/login">登录</router-link>
        <router-link to="/register">注册</router-link>
      </div>
    </el-header>
    
    <el-main class="main">
      <router-view />
    </el-main>
    
    <el-footer class="footer">
      <p>© 2026 电商平台 - 数据库课程设计</p>
    </el-footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { removeToken } from '@/utils/auth'

const router = useRouter()
const userStore = useUserStore()

const user = computed(() => userStore.user)
const isLoggedIn = computed(() => userStore.isLoggedIn)
const cartCount = ref(0)

const handleLogout = () => {
  userStore.logout()
  removeToken()
  router.push('/')
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
  padding: 0 50px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  height: 60px;
  
  .logo {
    font-size: 24px;
    font-weight: bold;
    color: #ff6700;
  }
  
  .nav {
    display: flex;
    gap: 30px;
    
    a {
      padding: 0 15px;
      line-height: 60px;
      color: #333;
      
      &:hover {
        color: #ff6700;
      }
    }
  }
  
  .user-info {
    .user-name {
      cursor: pointer;
      color: #ff6700;
    }
  }
  
  .auth-buttons {
    a {
      margin-left: 20px;
      color: #666;
      
      &:hover {
        color: #ff6700;
      }
    }
  }
}

.main {
  flex: 1;
  background: #f5f5f5;
}

.footer {
  text-align: center;
  background: #fff;
  border-top: 1px solid #f0f0f0;
  padding: 20px;
  color: #999;
}
</style>
