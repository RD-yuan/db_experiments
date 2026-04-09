<template>
  <div class="addresses-page">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>地址管理</span>
          <el-button type="primary" size="small">新增地址</el-button>
        </div>
      </template>
      <el-table :data="[]" style="width: 100%">
        <el-table-column prop="receiver" label="收件人" width="120" />
        <el-table-column prop="phone" label="电话" width="150" />
        <el-table-column prop="address" label="地址" />
        <el-table-column label="操作" width="150">
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
