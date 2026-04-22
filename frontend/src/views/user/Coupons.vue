<template>
  <div class="my-coupons">
    <el-card>
      <template #header>
        <div class="header">
          <span>我的优惠券</span>
          <el-radio-group v-model="statusFilter" size="small" @change="loadCoupons">
            <el-radio-button :value="0">未使用</el-radio-button>
            <el-radio-button :value="1">已使用</el-radio-button>
            <el-radio-button :value="2">已过期</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div v-loading="loading">
        <el-empty v-if="coupons.length === 0" description="暂无优惠券" />
        <div v-else class="coupon-list">
          <div v-for="item in coupons" :key="item.user_coupon_id" class="coupon-item" :class="{ used: item.status !== 0 }">
            <div class="coupon-left">
              <div class="coupon-value">
                <span v-if="item.coupon.type === 1">¥{{ item.coupon.value }}</span>
                <span v-else-if="item.coupon.type === 2">{{ item.coupon.value * 10 }}折</span>
                <span v-else>¥{{ item.coupon.value }}</span>
              </div>
              <div class="coupon-condition" v-if="item.coupon.min_order_amount > 0">
                满{{ item.coupon.min_order_amount }}可用
              </div>
              <div class="coupon-condition" v-else>无门槛</div>
            </div>
            <div class="coupon-right">
              <h4>{{ item.coupon.name }}</h4>
              <p class="coupon-time">
                有效期：{{ formatDate(item.coupon.start_time) }} ~ {{ formatDate(item.coupon.end_time) }}
              </p>
              <p v-if="item.coupon.is_vip_only" class="coupon-vip">VIP专享</p>
              <p class="coupon-status">
                <el-tag v-if="item.status === 0" type="success">未使用</el-tag>
                <el-tag v-else-if="item.status === 1" type="info">已使用</el-tag>
                <el-tag v-else type="danger">已过期</el-tag>
              </p>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/api'
import dayjs from 'dayjs'

const loading = ref(false)
const coupons = ref([])
const statusFilter = ref(0)

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD')

const loadCoupons = async () => {
  loading.value = true
  try {
    const res = await api.coupon.getMy(statusFilter.value)
    coupons.value = res || []
  } catch (error) {
    console.error('加载优惠券失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(loadCoupons)
</script>

<style scoped>
.my-coupons {
  padding: 10px 0;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.coupon-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.coupon-item {
  display: flex;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}
.coupon-item.used {
  opacity: 0.7;
  filter: grayscale(0.5);
}
.coupon-left {
  width: 160px;
  background: #ff6700;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
}
.coupon-value {
  font-size: 32px;
  font-weight: bold;
}
.coupon-condition {
  font-size: 14px;
  margin-top: 8px;
}
.coupon-right {
  flex: 1;
  padding: 20px;
}
.coupon-right h4 {
  margin: 0 0 10px;
  font-size: 18px;
}
.coupon-time {
  color: #909399;
  font-size: 13px;
  margin: 5px 0;
}
.coupon-vip {
  color: #e6a23c;
  font-size: 13px;
  margin: 5px 0;
}
.coupon-status {
  margin-top: 10px;
}
</style>