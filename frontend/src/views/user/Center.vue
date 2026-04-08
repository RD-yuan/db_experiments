<template>
  <div class="user-center">
    <el-row :gutter="20">
      <!-- 左侧菜单 -->
      <el-col :span="5">
        <el-card class="menu-card">
          <el-menu :default-active="$route.path" router>
            <el-menu-item index="/user/profile">
              <el-icon><User /></el-icon>
              <span>个人信息</span>
            </el-menu-item>
            <el-menu-item index="/user/addresses">
              <el-icon><Location /></el-icon>
              <span>地址管理</span>
            </el-menu-item>
            <el-menu-item index="/user/stats">
              <el-icon><TrendCharts /></el-icon>
              <span>消费统计</span>
            </el-menu-item>
            <el-menu-item index="/user/coupons">
              <el-icon><Ticket /></el-icon>
              <span>我的优惠券</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>
      
      <!-- 右侧内容 -->
      <el-col :span="19">
        <router-view />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
</script>

<style lang="scss" scoped>
.user-center {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.menu-card {
  :deep(.el-card__body) {
    padding: 0;
  }
  
  :deep(.el-menu) {
    border-right: none;
  }
}
</style>
