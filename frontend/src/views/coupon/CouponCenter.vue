<template>
  <div class="coupon-center">
    <el-card>
      <template #header>
        <span>领券中心</span>
      </template>
      <div v-loading="loading">
        <el-empty v-if="coupons.length === 0" description="暂无可领取优惠券" />
        <div v-else class="coupon-list">
          <div v-for="item in coupons" :key="item.coupon_id" class="coupon-item">
            <div class="coupon-left">
              <div class="coupon-value">
                <span v-if="item.type === 1">¥{{ item.value }}</span>
                <span v-else-if="item.type === 2">{{ item.value * 10 }}折</span>
                <span v-else>¥{{ item.value }}</span>
              </div>
              <div class="coupon-condition" v-if="item.min_order_amount > 0">
                满{{ item.min_order_amount }}可用
              </div>
              <div class="coupon-condition" v-else>无门槛</div>
            </div>
            <div class="coupon-right">
              <h4>{{ item.name }}</h4>
              <p class="coupon-time">有效期：{{ formatDate(item.start_time) }} ~ {{ formatDate(item.end_time) }}</p>
              <p v-if="item.is_vip_only" class="coupon-vip">VIP专享</p>
              <p class="coupon-limit">
                每人限领 {{ item.per_user_limit }} 张，
                已领 {{ item.received }} 张
              </p>
              <el-button
                type="primary"
                :disabled="!item.can_receive"
                @click="handleReceive(item)"
              >
                {{ item.can_receive ? '立即领取' : '已领取' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
import dayjs from 'dayjs'

const loading = ref(false)
const coupons = ref([])

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD')

const loadCoupons = async () => {
  loading.value = true
  try {
    const res = await api.coupon.getAvailable()
    coupons.value = res || []
  } catch (error) {
    console.error('加载优惠券失败', error)
  } finally {
    loading.value = false
  }
}

const handleReceive = async (coupon) => {
  try {
    await api.coupon.receive(coupon.coupon_id)
    ElMessage.success('领取成功')
    loadCoupons()
  } catch (error) {
    // 错误已由拦截器处理
  }
}

onMounted(loadCoupons)
</script>

<style scoped>
.coupon-center {
  max-width: 900px;
  margin: 20px auto;
  padding: 20px;
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
.coupon-limit {
  color: #606266;
  font-size: 13px;
  margin: 5px 0 15px;
}
</style>