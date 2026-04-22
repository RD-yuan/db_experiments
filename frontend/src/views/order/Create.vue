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

      <!-- 优惠券选择 -->
      <div class="section coupon-section">
        <div class="coupon-header">
          <span>优惠券</span>
          <el-button text type="primary" @click="showCouponDialog = true">
            {{ selectedCoupon ? '更换优惠券' : '选择优惠券' }}
            <span v-if="availableCouponsCount > 0">({{ availableCouponsCount }}张可用)</span>
          </el-button>
        </div>
        <div v-if="selectedCoupon" class="selected-coupon">
          <el-tag type="warning" closable @close="selectedCoupon = null">
            {{ selectedCoupon.coupon.name }} 省¥{{ selectedCoupon.discount.toFixed(2) }}
          </el-tag>
        </div>
      </div>

      <!-- 积分使用 -->
      <div class="section points-section">
        <div class="points-info">
          <span>我的积分：<strong>{{ userPoints }}</strong> (可抵扣 ¥{{ maxPointsDiscount.toFixed(2) }})</span>
        </div>
        <div class="points-use">
          <span>使用积分：</span>
          <el-input-number
            v-model="pointsToUse"
            :min="0"
            :max="maxUsablePoints"
            :step="100"
            controls-position="right"
            style="width: 180px"
          />
          <span class="points-tip">100积分=1元</span>
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
          <span class="price">¥{{ finalPaymentAmount.toFixed(2) }}</span>
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
    <!-- 优惠券选择对话框 -->
    <el-dialog v-model="showCouponDialog" title="选择优惠券" width="600px">
      <div v-if="availableCoupons.length === 0">
        <el-empty description="暂无可用优惠券" />
      </div>
      <el-radio-group v-model="selectedCouponId" class="coupon-radio-group">
        <el-radio
          v-for="uc in availableCoupons"
          :key="uc.user_coupon_id"
          :label="uc.user_coupon_id"
          border
          class="coupon-radio-item"
        >
          <div class="dialog-coupon-info">
            <div class="coupon-main">
              <span class="coupon-name">{{ uc.coupon.name }}</span>
              <span class="coupon-discount">省¥{{ computeCouponDiscount(uc).toFixed(2) }}</span>
            </div>
            <div class="coupon-meta">
              <span>有效期至 {{ formatDate(uc.coupon.end_time) }}</span>
            </div>
          </div>
        </el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="showCouponDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmCouponSelection">确定</el-button>
      </template>
    </el-dialog>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import dayjs from 'dayjs'
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
    const pointsToUse = ref(0)

    const userPoints = computed(() => userStore.user?.points || 0)
    const maxPointsDiscount = computed(() => {
      return Math.min(userPoints.value * 0.01, totalAmount.value * 0.5)
    })
    const maxUsablePoints = computed(() => Math.floor(maxPointsDiscount.value * 100))

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

    const formatDate = (date) => {
      if (!date) return ''
      return dayjs(date).format('YYYY-MM-DD')
    }

    const getEffectivePrice = (product) => {
      if (hasActiveVip.value && hasProductVipPrice(product)) {
        return Number(product.vip_price)
      }
      return Number(product?.price || 0)
    }

    // ========== 优惠券相关 ==========
    const showCouponDialog = ref(false)
    const availableCoupons = ref([])
    const selectedCoupon = ref(null)
    const selectedCouponId = ref(null)   // 确保定义

    const availableCouponsCount = computed(() => availableCoupons.value.length)

    const loadAvailableCoupons = async () => {
      try {
        const res = await api.coupon.getMy(0)
        const allCoupons = res || []
        const now = new Date()
        availableCoupons.value = allCoupons.filter(uc => {
          const coupon = uc.coupon
          if (!coupon) return false
          const start = new Date(coupon.start_time)
          const end = new Date(coupon.end_time)
          if (now < start || now > end) return false
          if (coupon.is_vip_only && !hasActiveVip.value) return false
          if (coupon.min_order_amount > totalAmount.value) return false
          return true
        })
      } catch (error) {
        console.error('加载优惠券失败', error)
      }
    }

    const computeCouponDiscount = (userCoupon) => {
      const coupon = userCoupon.coupon
      const total = totalAmount.value
      if (coupon.type === 1) {
        return total >= coupon.min_order_amount ? Number(coupon.value) : 0
      } else if (coupon.type === 2) {
        if (total < coupon.min_order_amount) return 0
        let discount = total * (1 - coupon.value)
        if (coupon.max_discount) discount = Math.min(discount, coupon.max_discount)
        return discount
      } else if (coupon.type === 3) {
        return total >= coupon.min_order_amount ? Number(coupon.value) : 0
      }
      return 0
    }

    const selectCoupon = (userCoupon) => {
      selectedCoupon.value = {
        ...userCoupon,
        discount: computeCouponDiscount(userCoupon)
      }
      showCouponDialog.value = false
    }

    const confirmCouponSelection = () => {
      if (!selectedCouponId.value) {
        ElMessage.warning('请选择一张优惠券')
        return
      }
      const uc = availableCoupons.value.find(c => c.user_coupon_id === selectedCouponId.value)
      if (uc) selectCoupon(uc)
    }

    const finalPaymentAmount = computed(() => {
      const pointsDiscount = pointsToUse.value * 0.01
      const base = totalAmount.value + freight.value - pointsDiscount
      const couponDiscount = selectedCoupon.value?.discount || 0
      return Math.max(0, base - couponDiscount)
    })

    // 从路由 query 获取 cart_ids 并加载购物车中选中的商品
    const loadCartItems = async () => {
      const cartIds = route.query.cart_ids
      if (!cartIds) {
        ElMessage.error('请从购物车结算')
        router.replace('/cart')
        return
      }

      try {
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
          cart_ids: cartIds,
          points_used: pointsToUse.value,
          coupon_id: selectedCoupon.value?.user_coupon_id
        })
        ElMessage.success('订单创建成功')
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
      await loadAvailableCoupons()
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
      submitOrder,
      pointsToUse,
      userPoints,
      maxPointsDiscount,
      maxUsablePoints,
      showCouponDialog,
      availableCoupons,
      selectedCoupon,
      selectedCouponId,
      availableCouponsCount,
      loadAvailableCoupons,
      computeCouponDiscount,
      selectCoupon,
      confirmCouponSelection,
      formatDate,
      finalPaymentAmount
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

.points-section {
  background: #f9f9f9;
  padding: 15px 20px;
  border-radius: 8px;
  .points-info { margin-bottom: 10px; }
  .points-use {
    display: flex;
    align-items: center;
    gap: 15px;
    .points-tip { color: #999; font-size: 13px; }
  }
}

.coupon-section {
  background: #f9f9f9;
  padding: 15px 20px;
  border-radius: 8px;
  .coupon-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
  }
  .selected-coupon {
    margin-top: 10px;
  }
}

.coupon-radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.coupon-radio-item {
  padding: 15px !important;
  height: auto !important;
}

.dialog-coupon-info {
  width: 100%;
  .coupon-main {
    display: flex;
    justify-content: space-between;
    font-weight: 500;
    .coupon-discount {
      color: #ff6700;
    }
  }
  .coupon-meta {
    margin-top: 8px;
    color: #909399;
    font-size: 12px;
  }
}
</style>
