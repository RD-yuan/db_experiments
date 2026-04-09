<template>
  <div class="order-detail">
    <el-card>
      <template #header>
        <span>订单详情 #{{ $route.params.id }}</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ $route.params.id }}</el-descriptions-item>
        <el-descriptions-item label="状态">待支付</el-descriptions-item>
        <el-descriptions-item label="创建时间">-</el-descriptions-item>
        <el-descriptions-item label="总价">¥0.00</el-descriptions-item>
      </el-descriptions>

      <h3 style="margin-top: 20px">商品列表</h3>
      <el-table :data="[]" style="width: 100%">
        <el-table-column prop="name" label="商品名称" />
        <el-table-column prop="price" label="单价" width="120" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="subtotal" label="小计" width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
</script>
