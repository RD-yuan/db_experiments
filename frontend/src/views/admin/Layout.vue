<template>
  <div class="admin-layout">
    <el-container>
      <el-aside width="200px">
        <el-menu
          :default-active="$route.path"
          router
        >
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

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
</script>

<style lang="scss" scoped>
.admin-layout {
  min-height: 100vh;
}

.el-aside {
  background: #001524;
  overflow: hidden;

  :deep(.el-menu) {
    border-right: none;
    background: #001524;
    color: #bfdbfe;
  }

  :deep(.el-menu-item) {
    color: #bfdbfe;

    &:hover {
      background: #002140;
    }

    &.is-active {
      background: #ff6700;
      color: #fff;
    }
  }
}

.el-main {
  background: #f0f2f8;
  padding: 20px;
  overflow-y: auto;
}
</style>
