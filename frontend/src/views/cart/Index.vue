<template>
  <div class="cart-page">
    <div class="page-title">我的购物车</div>

    <div class="cart-container" v-loading="loading">
      <div class="cart-main">
        <div v-if="cartItems.length === 0" class="empty-cart">
          <el-empty description="购物车是空的">
            <el-button type="primary" @click="$router.push('/products')">去购物</el-button>
          </el-empty>
        </div>

        <template v-else>
          <!-- 异常商品提示 -->
          <div v-if="problemItems.length > 0" class="problem-banner">
            <el-icon><WarningFilled /></el-icon>
            <span>有 {{ problemItems.length }} 件商品存在问题（已下架或库存不足），请及时清理</span>
            <el-button size="small" type="danger" text @click="clearProblems">一键清理</el-button>
          </div>

          <!-- 全选 / 批量删除 -->
          <div class="cart-toolbar">
            <el-checkbox v-model="selectAll" :indeterminate="isIndeterminate" @change="handleSelectAll">
              全选
            </el-checkbox>
            <el-button size="small" type="danger" text :disabled="selectedIds.length === 0" @click="batchDelete">
              删除选中 ({{ selectedIds.length }})
            </el-button>
          </div>

          <div class="cart-list">
            <div v-for="item in cartItems" :key="item.cart_id" class="cart-item" :class="{ 'is-problem': item._problem }">
              <el-checkbox
                v-model="item.selected"
                :disabled="item._problem"
                @change="handleSelectChange(item)"
              />

              <div class="product-image" @click="!item._problem && goToProduct(item.product.product_id)">
                <el-image :src="item.product.main_image" fit="contain" />
              </div>

              <div class="product-info">
                <h3 @click="!item._problem && goToProduct(item.product.product_id)">
                  {{ item.product.name }}
                  <span v-if="item.sku_spec_text" class="sku-spec">{{ item.sku_spec_text }}</span>
                </h3>
                <div class="product-price">
                  <span class="current">¥{{ getEffectivePrice(item).toFixed(2) }}</span>
                  <span class="original" v-if="hasActiveVip && hasProductVipPrice(item.product)">
                    ¥{{ Number(item.product.price || 0).toFixed(2) }}
                  </span>
                </div>
                <!-- 异常标记 -->
                <div v-if="item._problem" class="problem-tag">
                  <el-tag :type="item._problemType === 'offline' ? 'danger' : 'warning'" size="small">
                    {{ item._problemType === 'offline' ? '已下架' : '库存不足' }}
                  </el-tag>
                </div>
              </div>

              <div class="quantity-control">
                <el-input-number
                  v-model="item.quantity"
                  :min="1"
                  :max="item.product.available_stock > 0 ? item.product.available_stock : 1"
                  :disabled="item._problem"
                  @change="handleQuantityChange(item)"
                />
              </div>

              <div class="subtotal">
                ¥{{ (getEffectivePrice(item) * item.quantity).toFixed(2) }}
              </div>

              <div class="actions">
                <el-button type="danger" text @click="handleRemove(item.cart_id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 金额汇总 -->
      <div class="cart-summary" v-if="cartItems.length > 0">
        <div class="summary-row">
          <span>商品总数</span>
          <span>{{ selectedCount }} 件</span>
        </div>
        <div class="summary-row">
          <span>商品金额</span>
          <span>¥{{ selectedAmount.toFixed(2) }}</span>
        </div>
        <div class="summary-row">
          <span>预估运费</span>
          <span>{{ freightText }}</span>
        </div>
        <div class="summary-row" v-if="discount > 0">
          <span>优惠抵扣</span>
          <span class="discount">-¥{{ discount.toFixed(2) }}</span>
        </div>
        <div class="summary-row total">
          <span>预估应付</span>
          <span class="amount">¥{{ estimatedTotal.toFixed(2) }}</span>
        </div>

        <el-button
          type="primary" size="large"
          :disabled="selectedCount === 0 || hasProblemSelected"
          @click="handleCheckout"
          class="checkout-btn"
        >
          结算 ({{ selectedCount }})
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const cartItems = ref([])

const hasActiveVip = computed(() => {
  const user = userStore.user
  if (!user?.vip_active) return false
  if (!user.vip_expire_time) return true
  return new Date(user.vip_expire_time).getTime() > Date.now()
})

const vipDiscountFactor = computed(() => {
  const level = userStore.user?.vip_level || 0
  const factors = { 1: 1.0, 2: 0.95, 3: 0.9 }
  return factors[level] || 1.0
})

const hasProductVipPrice = (product) => {
  const vipPrice = Number(product?.vip_price || 0)
  const price = Number(product?.price || 0)
  return vipPrice > 0 && vipPrice < price
}

const getEffectivePrice = (item) => {
  if (item?.effective_price !== undefined && item?.effective_price !== null) {
    return Number(item.effective_price)
  }
  const product = item?.product || item
  let base = Number(item?.sku_price || product?.price || 0)
  if (hasActiveVip.value) {
    const skuVip = Number(item?.sku_vip_price || 0)
    const productVip = Number(product?.vip_price || 0)
    if (skuVip > 0 && skuVip < base) base = skuVip
    else if (productVip > 0 && productVip < Number(product?.price || 0)) base = productVip
    base = base * vipDiscountFactor.value
  }
  return base
}

// ---- 异常检测 ----
const problemItems = computed(() => cartItems.value.filter(i => i._problem))
const hasProblemSelected = computed(() => cartItems.value.some(i => i.selected && i._problem))

const markProblems = () => {
  for (const item of cartItems.value) {
    const p = item.product
    if (p && p.status !== 1) {
      item._problem = true
      item._problemType = 'offline'
      item.selected = false
    } else if (p && (p.available_stock || 0) <= 0) {
      item._problem = true
      item._problemType = 'nostock'
      item.selected = false
    } else {
      item._problem = false
      item._problemType = null
    }
  }
}

const clearProblems = async () => {
  const ids = problemItems.value.map(i => i.cart_id)
  if (ids.length === 0) return
  try {
    await ElMessageBox.confirm(`确定要移除 ${ids.length} 件异常商品吗？`, '清理购物车')
    for (const id of ids) {
      try { await api.cart.delete(id) } catch { /* ignore single delete failure */ }
    }
    ElMessage.success('已清理')
    loadCart()
  } catch { /* user cancelled */ }
}

// ---- 全选 / 批量 ----
const selectAll = computed({
  get: () => cartItems.value.length > 0 && cartItems.value.filter(i => !i._problem).every(i => i.selected),
  set: (val) => {}
})
const isIndeterminate = computed(() => {
  const valid = cartItems.value.filter(i => !i._problem)
  const sel = valid.filter(i => i.selected).length
  return sel > 0 && sel < valid.length
})
const selectedIds = computed(() => cartItems.value.filter(i => i.selected).map(i => i.cart_id))

const handleSelectAll = async (val) => {
  for (const item of cartItems.value) {
    if (item._problem) continue
    if (item.selected !== val) {
      item.selected = val
      try { await api.cart.update(item.cart_id, { selected: val ? 1 : 0 }) } catch { /* ignore */ }
    }
  }
}

const batchDelete = async () => {
  const ids = selectedIds.value
  if (ids.length === 0) return
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${ids.length} 件商品吗？`, '批量删除')
    for (const id of ids) {
      try { await api.cart.delete(id) } catch { /* ignore single failure */ }
    }
    ElMessage.success('删除成功')
    loadCart()
  } catch { /* user cancelled */ }
}

// ---- 金额 ----
const selectedCount = computed(() => {
  return cartItems.value.filter(item => item.selected).reduce((sum, item) => sum + item.quantity, 0)
})

const selectedAmount = computed(() => {
  return cartItems.value.filter(item => item.selected).reduce((sum, item) => {
    return sum + getEffectivePrice(item) * item.quantity
  }, 0)
})

const discount = ref(0)
const freight = computed(() => selectedAmount.value >= 300 ? 0 : 12)
const freightText = computed(() => freight.value === 0 ? '包邮' : `¥${freight.value.toFixed(2)}`)
const estimatedTotal = computed(() => Math.max(0, selectedAmount.value - discount.value + freight.value))

// ---- 数据加载 ----
const loadCart = async () => {
  loading.value = true
  try {
    const data = await api.cart.getList()
    cartItems.value = (data.items || []).map(item => ({ ...item, _problem: false, _problemType: null }))
    markProblems()
  } catch (error) {
    console.error('加载购物车失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSelectChange = async (item) => {
  try {
    await api.cart.update(item.cart_id, { selected: item.selected ? 1 : 0 })
  } catch (error) {
    console.error('更新失败:', error)
  }
}

const handleQuantityChange = async (item) => {
  try {
    await api.cart.update(item.cart_id, { quantity: item.quantity })
    loadCart() // reload to refresh effective_price
  } catch (error) {
    console.error('更新数量失败:', error)
    loadCart()
  }
}

const handleRemove = async (cartId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个商品吗?', '提示')
    await api.cart.delete(cartId)
    ElMessage.success('删除成功')
    loadCart()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

const goToProduct = (productId) => {
  router.push(`/product/${productId}`)
}

const handleCheckout = () => {
  const selectedItems = cartItems.value.filter(item => item.selected && !item._problem)
  if (selectedItems.length === 0) {
    ElMessage.warning('请选择要结算的商品')
    return
  }
  router.push({
    path: '/orders/create',
    query: {
      cart_ids: selectedItems.map(item => item.cart_id).join(',')
    }
  })
}

onMounted(() => { loadCart() })
</script>

<style lang="scss" scoped>
.cart-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.cart-container {
  display: flex;
  gap: 20px;
}

.cart-main {
  flex: 1;
}

.problem-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 8px;
  margin-bottom: 12px;
  color: #f56c6c;
  font-size: 14px;
}

.cart-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 20px;
  background: #fff;
  border-radius: 8px 8px 0 0;
  border-bottom: 1px solid #f0f0f0;
}

.cart-list {
  background: #fff;
  border-radius: 0 0 8px 8px;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;

  &:last-child {
    border-bottom: none;
  }

  &.is-problem {
    background: #fafafa;
    opacity: 0.7;
  }

  .product-image {
    width: 100px;
    height: 100px;
    margin: 0 20px;
    cursor: pointer;

    .el-image {
      width: 100%;
      height: 100%;
    }
  }

  .product-info {
    flex: 1;

    h3 {
      font-size: 16px;
      margin-bottom: 10px;
      cursor: pointer;

      &:hover {
        color: #ff6700;
      }

      .sku-spec {
        color: #999;
        font-size: 12px;
        margin-left: 8px;
      }
    }

    .product-price {
      .current {
        font-size: 18px;
        color: #ff6700;
        font-weight: bold;
      }

      .original {
        margin-left: 8px;
        font-size: 13px;
        color: #999;
        text-decoration: line-through;
      }
    }

    .problem-tag {
      margin-top: 6px;
    }
  }

  .quantity-control {
    margin: 0 20px;
  }

  .subtotal {
    width: 120px;
    text-align: right;
    font-size: 18px;
    font-weight: bold;
    color: #ff6700;
    margin-right: 20px;
  }

  .actions {
    width: 60px;
  }
}

.cart-summary {
  width: 300px;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  height: fit-content;
  position: sticky;
  top: 20px;

  .summary-row {
    display: flex;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;

    &.total {
      border-bottom: none;
      padding-top: 20px;
      font-size: 18px;

      .amount {
        color: #ff6700;
        font-size: 24px;
        font-weight: bold;
      }
    }

    .discount {
      color: #67c23a;
    }
  }

  .checkout-btn {
    width: 100%;
    margin-top: 20px;
    height: 50px;
    font-size: 18px;
    background-color: #ff6700;
    border-color: #ff6700;

    &:hover {
      background-color: #ff8533;
      border-color: #ff8533;
    }
  }
}

.empty-cart {
  background: #fff;
  padding: 100px 0;
  border-radius: 8px;
}
</style>
