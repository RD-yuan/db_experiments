<template>
  <div class="home-page">
    <el-carousel height="400px">
      <el-carousel-item v-for="i in 3" :key="i">
        <div class="banner" :style="{ background: colors[i - 1] }">
          <h1>欢迎来到电商平台</h1>
          <p>发现优质商品，享受便捷购物</p>
        </div>
      </el-carousel-item>
    </el-carousel>

    <div class="section" style="margin-top: 30px">
      <h2>热门商品</h2>
      <el-row :gutter="20">
        <el-col :span="6" v-for="item in products" :key="item.id">
          <el-card :body-style="{ padding: '0' }">
            <div style="height: 200px; background: #f5f5f5; display: flex; align-items: center; justify-content: center">
              商品图片
            </div>
            <div style="padding: 14px">
              <span>{{ item.name }}</span>
              <div class="price">¥{{ item.price }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const colors = ['#409eff', '#67c23a', '#e6a23c']

const products = ref([
  { id: 1, name: '示例商品1', price: 99.9 },
  { id: 2, name: '示例商品2', price: 199.9 },
  { id: 3, name: '示例商品3', price: 299.9 },
  { id: 4, name: '示例商品4', price: 399.9 }
])
</script>

<style scoped>
.banner {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
  margin-top: 8px;
}
</style>
