<template>
  <div class="order-create">
    <h2>确认订单</h2>
    <div v-loading="loading">
      <!-- 地址选择 -->
      <div class="section">
        <h3>收货地址</h3>
        <div v-if="addresses.length === 0">
          <el-empty description="暂无收货地址">
            <el-button type="primary" @click="$router.push('/user/addresses')">添加地址</el-button>
          </el-empty>
        </div>
        <el-radio-group v-else v-model="selectedAddressId" class="address-list">
          <el-radio v-for="addr in addresses" :key="addr.address_id" :label="addr.address_id" border>
            <div class="address-item">
              <div>{{ addr.recipient_name }} {{ addr.recipient_phone }}</div>
              <div class="address-detail">{{ addr.full_address }}</div>
            </div>
          </el-radio>
        </el-radio-group>
      </div>

      <!-- 商品清单 -->
      <div class="section">
        <h3>商品清单</h3>
        <div class="items-list">
          <div v-for="item in orderItems" :key="item.cart_id" class="order-item">
            <el-image :src="item.product.main_image" class="product-img" fit="contain" />
            <div class="product-info">
              <h4>{{ item.product.name }}</h4>
              <span>
                ¥{{ getEffectivePrice(item.product).toFixed(2) }} x {{ item.quantity }}
                <em v-if="hasActiveVip && hasProductVipPrice(item.product)">
                  会员价已生效，原价 ¥{{ Number(item.product.price || 0).toFixed(2) }}
                </em>
              </span>
            </div>
            <div class="item-total">¥{{ (getEffectivePrice(item.product) * item.quantity).toFixed(2) }}</div>
          </div>
        </div>
      </div>

      <!-- 金额汇总 -->
      <div class="section summary">
        <div class="summary-row">
          <span>商品总额</span>
          <span>¥{{ totalAmount.toFixed(2) }}</span>
        </div>
        <div class="summary-row">
          <span>运费</span>
          <span>¥{{ freight.toFixed(2) }}</span>
        </div>
        <div class="summary-row total">
          <span>应付总额</span>
          <span class="price">¥{{ (totalAmount + freight).toFixed(2) }}</span>
        </div>
      </div>

      <!-- 提交按钮 -->
      <div class="actions">
        <el-button @click="$router.back()">返回修改</el-button>
        <el-button type="primary" size="large" :disabled="!selectedAddressId" @click="submitOrder">
          提交订单
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'

export default {
  name: 'OrderCreate',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const userStore = useUserStore()
    const loading = ref(true)
    const addresses = ref([])
    const selectedAddressId = ref(null)
    const orderItems = ref([])

    const hasActiveVip = computed(() => {
      const user = userStore.user
      if (!user?.vip_active) return false
      if (!user.vip_expire_time) return true
      return new Date(user.vip_expire_time).getTime() > Date.now()
    })

    const hasProductVipPrice = (product) => {
      const vipPrice = Number(product?.vip_price || 0)
      const price = Number(product?.price || 0)
      return vipPrice > 0 && vipPrice < price
    }

    const getEffectivePrice = (product) => {
      if (hasActiveVip.value && hasProductVipPrice(product)) {
        return Number(product.vip_price)
      }
      return Number(product?.price || 0)
    }

    // 从路由 query 获取 cart_ids 并加载购物车中选中的商品
    const loadCartItems = async () => {
      const cartIds = route.query.cart_ids
      if (!cartIds) {
        ElMessage.error('请从购物车结算')
        router.replace('/cart')
        return
      }

      try {
        // 获取购物车列表，然后过滤出选中的商品
        const data = await api.cart.getList()
        const selectedIds = cartIds.split(',').map(Number)
        orderItems.value = data.items.filter(item => selectedIds.includes(item.cart_id) && item.selected)
        if (orderItems.value.length === 0) {
          ElMessage.warning('未找到结算商品')
          router.replace('/cart')
        }
      } catch (error) {
        ElMessage.error('加载商品失败')
        router.replace('/cart')
      }
    }

    // 加载地址列表
    const loadAddresses = async () => {
      try {
        const data = await api.user.getAddresses()
        addresses.value = data || []
        const defaultAddr = addresses.value.find(addr => addr.is_default)
        if (defaultAddr) selectedAddressId.value = defaultAddr.address_id
        else if (addresses.value.length > 0) selectedAddressId.value = addresses.value[0].address_id
      } catch (error) {
        console.error('加载地址失败', error)
      }
    }

    // 计算总金额
    const totalAmount = computed(() => {
      return orderItems.value.reduce((sum, item) => {
        return sum + getEffectivePrice(item.product) * item.quantity
      }, 0)
    })

    // 运费规则：满99包邮，否则10元
    const freight = computed(() => totalAmount.value >= 99 ? 0 : 10)

    // 提交订单
    const submitOrder = async () => {
      if (!selectedAddressId.value) {
        ElMessage.warning('请选择收货地址')
        return
      }
      const cartIds = orderItems.value.map(item => item.cart_id)
      try {
        loading.value = true
        const data = await api.order.create({
          address_id: selectedAddressId.value,
          cart_ids: cartIds
        })
        ElMessage.success('订单创建成功')
        // 跳转到订单详情或支付页，根据后端返回的 order_id
        router.replace(`/order/${String(data.order_id)}`)
      } catch (error) {
        ElMessage.error('订单创建失败：' + (error.message || '请稍后重试'))
      } finally {
        loading.value = false
      }
    }

    onMounted(async () => {
      await loadCartItems()
      await loadAddresses()
      loading.value = false
    })

    return {
      loading,
      addresses,
      selectedAddressId,
      orderItems,
      hasActiveVip,
      hasProductVipPrice,
      getEffectivePrice,
      totalAmount,
      freight,
      submitOrder
    }
  }
}
</script>

<style lang="scss" scoped>
.order-create {
  max-width: 1000px;
  margin: 20px auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}
.section {
  margin-top: 30px;
  h3 {
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
  }
}
.address-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  .el-radio {
    padding: 15px;
    height: auto;
  }
}
.address-item {
  .address-detail {
    color: #666;
    font-size: 13px;
    margin-top: 5px;
  }
}
.items-list {
  .order-item {
    display: flex;
    align-items: center;
    padding: 15px 0;
    border-bottom: 1px solid #f5f5f5;
    .product-img {
      width: 80px;
      height: 80px;
      margin-right: 20px;
    }
    .product-info {
      flex: 1;
      h4 { margin-bottom: 5px; }
      em {
        margin-left: 8px;
        color: #67c23a;
        font-size: 12px;
        font-style: normal;
      }
    }
    .item-total {
      font-weight: bold;
      color: #ff6700;
    }
  }
}
.summary {
  text-align: right;
  .summary-row {
    display: flex;
    justify-content: flex-end;
    gap: 50px;
    padding: 8px 0;
    &.total {
      font-size: 18px;
      font-weight: bold;
      .price { color: #ff6700; font-size: 22px; }
    }
  }
}
.actions {
  margin-top: 30px;
  display: flex;
  justify-content: flex-end;
  gap: 20px;
}
</style>
