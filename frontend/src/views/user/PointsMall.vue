<template>
  <div class="points-mall">
    <el-card>
      <template #header>
        <span>积分商城 · 我的积分：<strong>{{ userPoints }}</strong></span>
      </template>

      <el-row :gutter="20">
        <el-col v-for="item in products" :key="item.product_id" :span="8">
          <el-card class="product-card" shadow="hover">
            <el-image :src="item.main_image" fit="cover" class="product-img" />
            <div class="product-info">
              <h3>{{ item.name }}</h3>
              <p class="points-cost">{{ item.exchange_points }} 积分</p>
              <p class="stock" v-if="item.available_stock > 0">库存：{{ item.available_stock }}</p>
              <p class="stock" v-else style="color: #f56c6c">已售罄</p>
            </div>
            <el-button
              type="primary"
              :disabled="userPoints < item.exchange_points || item.available_stock === 0"
              @click="exchange(item)"
            >
              {{ item.available_stock > 0 ? '立即兑换' : '已售罄' }}
            </el-button>
          </el-card>
        </el-col>
      </el-row>

      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          :page-size="perPage"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadProducts"
        />
      </div>
    </el-card>

    <!-- 地址选择对话框 -->
    <el-dialog v-model="addressDialogVisible" title="选择收货地址" width="500px">
      <el-radio-group v-model="selectedAddressId" class="address-list">
        <el-radio v-for="addr in addresses" :key="addr.address_id" :label="addr.address_id" border>
          {{ addr.full_address }} ({{ addr.recipient_name }} {{ addr.recipient_phone }})
        </el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="addressDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmExchange">确认兑换</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const products = ref([])
const page = ref(1)
const perPage = ref(12)
const total = ref(0)
const userPoints = ref(0)

const addressDialogVisible = ref(false)
const addresses = ref([])
const selectedAddressId = ref(null)
const currentProduct = ref(null)

const loadProducts = async () => {
  try {
    const res = await api.product.getExchangeList({ page: page.value, per_page: perPage.value })
    products.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载商品失败', error)
  }
}

const loadAddresses = async () => {
  try {
    const res = await api.user.getAddresses()
    addresses.value = res || []
    if (addresses.value.length > 0) {
      const defaultAddr = addresses.value.find(addr => addr.is_default)
      selectedAddressId.value = defaultAddr ? defaultAddr.address_id : addresses.value[0].address_id
    }
  } catch (error) {
    console.error('加载地址失败', error)
  }
}

const exchange = async (product) => {
  currentProduct.value = product
  await loadAddresses()
  addressDialogVisible.value = true
}

const confirmExchange = async () => {
  if (!selectedAddressId.value) {
    ElMessage.warning('请选择收货地址')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定使用 ${currentProduct.value.exchange_points} 积分兑换“${currentProduct.value.name}”吗？`,
      '确认兑换'
    )
  } catch {
    return
  }

  try {
    await api.order.exchange({
      product_id: currentProduct.value.product_id,
      quantity: 1,
      address_id: selectedAddressId.value
    })
    ElMessage.success('兑换成功！')
    addressDialogVisible.value = false
    // 刷新用户积分
    await userStore.ensureSession(true)
    userPoints.value = userStore.user?.points || 0
    loadProducts()
  } catch (error) {
    // 错误已由拦截器处理
  }
}

onMounted(async () => {
  await userStore.ensureSession()
  userPoints.value = userStore.user?.points || 0
  loadProducts()
})
</script>

<style scoped>
.points-mall {
  padding: 10px 0;
}

.product-card {
  margin-bottom: 20px;
  text-align: center;
}

.product-img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.product-info {
  margin: 15px 0;
}

.product-info h3 {
  font-size: 16px;
  margin-bottom: 10px;
}

.points-cost {
  color: #ff6700;
  font-size: 20px;
  font-weight: bold;
  margin: 10px 0;
}

.stock {
  color: #909399;
  font-size: 13px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>