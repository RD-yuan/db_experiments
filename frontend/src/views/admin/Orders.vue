<template>
  <div class="admin-orders">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>订单管理</span>
          <el-input placeholder="搜索订单" style="width: 300px" />
        </div>
      </template>
      <el-table :data="[]" style="width: 100%">
        <el-table-column prop="id" label="订单号" width="120" />
        <el-table-column prop="user" label="用户" />
        <el-table-column prop="total" label="金额" width="120" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="created_at" label="下单时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default>
            <el-button size="small">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
</script>
