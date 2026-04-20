<template>
  <div class="order-detail" v-loading="loading">
    <el-card v-if="order">
      <template #header>
        <span>订单详情 #{{ order.order_id }}</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ order.order_id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType">{{ order.status_text }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(order.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="实付金额">¥{{ order.payment_amount }}</el-descriptions-item>
        <el-descriptions-item label="运费">¥{{ order.freight_amount }}</el-descriptions-item>
        <el-descriptions-item label="优惠金额">¥{{ order.discount_amount }}</el-descriptions-item>
        <el-descriptions-item v-if="order.points_used" label="使用积分">{{ order.points_used }}</el-descriptions-item>
        <el-descriptions-item v-if="order.address_snapshot" label="收货信息">
          {{ addressDisplay }}
        </el-descriptions-item>
      </el-descriptions>

      <h3 style="margin-top: 20px">商品列表</h3>
      <el-table :data="order.items" style="width: 100%">
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="price" label="单价" width="120">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column label="小计" width="120">
          <template #default="{ row }">¥{{ row.subtotal }}</template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 20px; text-align: right">
        <el-button v-if="order.status === 0" type="primary" @click="handlePay">立即支付</el-button>
        <el-button v-if="order.status === 0" @click="handleCancel">取消订单</el-button>
        <el-button v-if="order.status === 2" type="primary" @click="handleReceive">确认收货</el-button>
        <el-button @click="$router.back()">返回</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const order = ref(null)

const statusType = computed(() => {
  const types = { 0: 'warning', 1: 'primary', 2: 'info', 3: 'success', 4: 'info', 5: 'danger' }
  return types[order.value?.status] || 'info'
})

const addressDisplay = computed(() => {
  if (!order.value?.address_snapshot) return ''
  try {
    const addr = JSON.parse(order.value.address_snapshot)
    return `${addr.recipient_name} ${addr.recipient_phone} ${addr.full_address || addr.detail_address}`
  } catch {
    return order.value.address_snapshot
  }
})

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')

const loadOrder = async () => {
  loading.value = true
  try {
    const orderId = String(route.params.id)
    const data = await api.order.getDetail(orderId)
    order.value = data
  } catch (error) {
    ElMessage.error('订单不存在')
    router.replace('/orders')
  } finally {
    loading.value = false
  }
}

const handlePay = async () => {
  try {
    await api.order.pay(String(order.value.order_id))
    ElMessage.success('支付成功')
    loadOrder()
  } catch (error) {
    console.error('支付失败:', error)
  }
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm('确定要取消订单吗?', '提示')
    await api.order.cancel(String(order.value.order_id))
    ElMessage.success('订单已取消')
    loadOrder()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消订单失败:', error)
    }
  }
}

const handleReceive = async () => {
  try {
    await ElMessageBox.confirm('确认已收到商品吗?', '提示')
    await api.order.receive(String(order.value.order_id))
    ElMessage.success('确认收货成功')
    loadOrder()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('确认收货失败:', error)
    }
  }
}

onMounted(loadOrder)
</script>