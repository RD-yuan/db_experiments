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
        
        <div v-else class="cart-list">
          <div v-for="item in cartItems" :key="item.cart_id" class="cart-item">
            <el-checkbox v-model="item.selected" @change="handleSelectChange(item)" />
            
            <div class="product-image" @click="goToProduct(item.product.product_id)">
              <el-image :src="item.product.main_image" fit="contain" />
            </div>
            
            <div class="product-info">
              <h3 @click="goToProduct(item.product.product_id)">{{ item.product.name }}</h3>
              <div class="product-price">
                <span class="current">¥{{ item.product.price }}</span>
                <span class="vip" v-if="item.product.vip_price">VIP: ¥{{ item.product.vip_price }}</span>
              </div>
            </div>
            
            <div class="quantity-control">
              <el-input-number
                v-model="item.quantity"
                :min="1"
                :max="item.product.available_stock"
                @change="handleQuantityChange(item)"
              />
            </div>
            
            <div class="subtotal">
              ¥{{ (item.product.price * item.quantity).toFixed(2) }}
            </div>
            
            <div class="actions">
              <el-button type="danger" text @click="handleRemove(item.cart_id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="cart-summary" v-if="cartItems.length > 0">
        <div class="summary-row">
          <span>商品总数</span>
          <span>{{ selectedCount }} 件</span>
        </div>
        <div class="summary-row">
          <span>商品金额</span>
          <span>¥{{ selectedAmount.toFixed(2) }}</span>
        </div>
        <div class="summary-row" v-if="discount > 0">
          <span>优惠</span>
          <span class="discount">-¥{{ discount.toFixed(2) }}</span>
        </div>
        <div class="summary-row total">
          <span>应付金额</span>
          <span class="amount">¥{{ finalAmount.toFixed(2) }}</span>
        </div>
        
        <el-button type="primary" size="large" :disabled="selectedCount === 0" @click="handleCheckout" class="checkout-btn">
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

const router = useRouter()
const loading = ref(false)
const cartItems = ref([])

const selectedCount = computed(() => {
  return cartItems.value.filter(item => item.selected).reduce((sum, item) => sum + item.quantity, 0)
})

const selectedAmount = computed(() => {
  return cartItems.value.filter(item => item.selected).reduce((sum, item) => {
    return sum + item.product.price * item.quantity
  }, 0)
})

const discount = ref(0)
const finalAmount = computed(() => selectedAmount.value - discount.value)

const loadCart = async () => {
  loading.value = true
  try {
    const data = await api.cart.getList()
    cartItems.value = data.items || []
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
  } catch (error) {
    console.error('更新数量失败:', error)
    loadCart() // 重新加载
  }
}

const handleRemove = async (cartId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个商品吗?', '提示')
    await api.cart.delete(cartId)
    ElMessage.success('删除成功')
    loadCart()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

const goToProduct = (productId) => {
  router.push(`/product/${productId}`)
}

const handleCheckout = () => {
  const selectedItems = cartItems.value.filter(item => item.selected)
  if (selectedItems.length === 0) {
    ElMessage.warning('请选择要结算的商品')
    return
  }
  
  // 跳转到订单确认页
  router.push({
    path: '/orders/create',
    query: {
      cart_ids: selectedItems.map(item => item.cart_id).join(',')
    }
  })
}

onMounted(() => {
  loadCart()
})
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

.cart-list {
  background: #fff;
  border-radius: 8px;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  
  &:last-child {
    border-bottom: none;
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
    }
    
    .product-price {
      .current {
        font-size: 18px;
        color: #ff6700;
        font-weight: bold;
      }
      
      .vip {
        margin-left: 10px;
        font-size: 14px;
        color: #ff6700;
        padding: 2px 8px;
        border: 1px solid #ff6700;
        border-radius: 4px;
      }
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
