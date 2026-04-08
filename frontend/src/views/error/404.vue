<template>
  <div class="not-found">
    <h1>404</h1>
    <p>抱歉，您访问的页面不存在</p>
    <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
  </div>
</template>

<script setup>
</script>

<style lang="scss" scoped>
.not-found {
  text-align: center;
  padding: 100px 20px;
  
  h1 {
    font-size: 72px;
    color: #ff6700;
    margin-bottom: 20px;
  }
  
  p {
    font-size: 18px;
    color: #999;
    margin-bottom: 30px;
  }
}
</style>
