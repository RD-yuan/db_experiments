<template>
  <div class="admin-coupons">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>优惠券管理</span>
          <el-button type="primary">创建优惠券</el-button>
        </div>
      </template>
      <el-table :data="[]" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="value" label="优惠金额" width="120" />
        <el-table-column prop="min_spend" label="最低消费" width="120" />
        <el-table-column prop="valid_until" label="有效期至" width="180" />
        <el-table-column label="操作" width="200">
          <template #default>
            <el-button size="small">编辑</el-button>
            <el-button size="small" type="danger">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
</script>
