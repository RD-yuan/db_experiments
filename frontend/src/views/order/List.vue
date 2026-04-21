<template>
  <div class="order-list">
    <div class="page-title">我的订单</div>

    <!-- 订单状态筛选 -->
    <el-tabs v-model="activeStatus" @tab-change="handleTabChange">
      <el-tab-pane label="全部" name="all" />
      <el-tab-pane label="待支付" name="0" />
      <el-tab-pane label="已支付" name="1" />
      <el-tab-pane label="已发货" name="2" />
      <el-tab-pane label="已完成" name="3" />
      <el-tab-pane label="已取消" name="4" />
    </el-tabs>

    <div class="orders" v-loading="loading">
      <div v-if="orders.length === 0" class="empty-orders">
        <el-empty description="暂无订单" />
      </div>

      <div v-for="order in orders" :key="order.order_id" class="order-card">
        <div class="order-header">
          <div class="order-info">
            <span class="order-id">订单号: {{ order.order_id }}</span>
            <span class="order-time">{{ formatDate(order.create_time) }}</span>
          </div>
          <el-tag :type="getStatusType(order.status)">{{ order.status_text }}</el-tag>
        </div>

        <div class="order-items">
          <div v-for="item in order.items" :key="item.order_item_id" class="order-item">
            <el-image :src="item.product_image" fit="contain" class="product-image" />
            <div class="product-info">
              <h4>{{ item.product_name }}</h4>
              <p>¥{{ item.price }} x {{ item.quantity }}</p>
            </div>
            <div class="subtotal">¥{{ item.subtotal }}</div>
          </div>
        </div>

        <div class="order-footer">
          <div class="order-amount">
            共 {{ order.items.length }} 件商品 实付:
            <span class="amount">¥{{ order.payment_amount }}</span>
          </div>

          <div class="order-actions">
            <el-button v-if="order.status === 0" type="primary" @click="handlePay(String(order.order_id))">
              立即支付
            </el-button>
            <el-button v-if="order.status === 0" @click="handleCancel(String(order.order_id))">
              取消订单
            </el-button>
            <el-button v-if="order.status === 2" type="primary" @click="handleReceive(String(order.order_id))">
              确认收货
            </el-button>
            <el-button v-if="order.status === 3" @click="goToReview(String(order.order_id))">
              去评价
            </el-button>
            <el-button @click="goToDetail(String(order.order_id))">查看详情</el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="pagination-wrapper" v-if="total > 0">
      <el-pagination
        v-model:current-page="page"
        :page-size="10"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadOrders"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const orders = ref([])
const activeStatus = ref('all')
const page = ref(1)
const total = ref(0)

const loadOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      per_page: 10
    }

    if (activeStatus.value !== 'all') {
      params.status = activeStatus.value
    }

    const data = await api.order.getList(params)
    orders.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.error('加载订单失败:', error)
  } finally {
    loading.value = false
  }
}

const handleTabChange = () => {
  page.value = 1
  loadOrders()
}

const getStatusType = (status) => {
  const types = {
    0: 'warning',
    1: 'primary',
    2: 'info',
    3: 'success',
    4: 'info',
    5: 'danger'
  }
  return types[status] || 'info'
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const formatMoney = (value) => Number(value || 0).toFixed(2)

const handlePay = async (orderId) => {
  try {
    const order = orders.value.find(item => String(item.order_id) === String(orderId))
    await ElMessageBox.confirm(
      `将使用账户余额支付 ¥${formatMoney(order?.payment_amount)}，当前余额 ¥${formatMoney(userStore.user?.balance)}。确定支付吗？`,
      '余额支付',
      { type: 'warning' }
    )
    await api.order.pay(String(orderId))
    ElMessage.success('支付成功')
    await userStore.ensureSession(true)
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') console.error('支付失败:', error)
  }
}

const handleCancel = async (orderId) => {
  try {
    await ElMessageBox.confirm('确定要取消订单吗?', '提示')
    await api.order.cancel(String(orderId))
    ElMessage.success('订单已取消')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消订单失败:', error)
    }
  }
}

const handleReceive = async (orderId) => {
  try {
    await ElMessageBox.confirm('确认已收到商品吗?', '提示')
    await api.order.receive(String(orderId))
    ElMessage.success('确认收货成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('确认收货失败:', error)
    }
  }
}

const goToDetail = (orderId) => {
  router.push(`/order/${String(orderId)}`)
}

const goToReview = (orderId) => {
  router.push(`/order/${String(orderId)}?action=review`)
}

onMounted(() => {
  loadOrders()
})
</script>

<style lang="scss" scoped>
.order-list {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.orders {
  margin-top: 20px;
}

.order-card {
  background: #fff;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;

  .order-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background: #f9f9f9;
    border-bottom: 1px solid #eee;

    .order-info {
      .order-id {
        font-weight: 500;
        margin-right: 20px;
      }

      .order-time {
        color: #999;
        font-size: 14px;
      }
    }
  }

  .order-items {
    padding: 15px 20px;

    .order-item {
      display: flex;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      .product-image {
        width: 80px;
        height: 80px;
        margin-right: 15px;
      }

      .product-info {
        flex: 1;

        h4 {
          font-size: 14px;
          margin-bottom: 5px;
        }

        p {
          font-size: 12px;
          color: #999;
        }
      }

      .subtotal {
        font-weight: bold;
        color: #ff6700;
      }
    }
  }

  .order-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-top: 1px solid #eee;

    .order-amount {
      font-size: 14px;

      .amount {
        font-size: 20px;
        font-weight: bold;
        color: #ff6700;
        margin-left: 5px;
      }
    }

    .order-actions {
      .el-button--primary {
        background-color: #ff6700;
        border-color: #ff6700;
      }
    }
  }
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>
