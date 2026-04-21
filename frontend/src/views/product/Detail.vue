<template>
  <div class="product-detail" v-loading="loading">
    <!-- 商品信息 -->
    <div class="product-main">
      <div class="product-gallery">
        <div class="main-image">
          <el-image :src="product.main_image || defaultImage" fit="contain" />
        </div>
        <div class="thumbnail-list" v-if="product.sub_images">
          <div v-for="(img, index) in subImages" :key="index" class="thumbnail-item">
            <el-image :src="img" fit="contain" @click="currentImage = img" />
          </div>
        </div>
      </div>
      
      <div class="product-info">
        <h1 class="product-title">{{ product.name }}</h1>
        
        <div class="product-subtitle" v-if="product.description">
          {{ product.description }}
        </div>
        
        <div class="price-section">
          <div class="price-row">
            <span class="label">价格</span>
            <span class="current-price">¥{{ displayPrice }}</span>
            <span class="original-price" v-if="hasActiveVip && hasVipPrice">
              ¥{{ product.price }}
            </span>
            <span class="original-price" v-else-if="product.original_price && product.original_price > product.price">
              ¥{{ product.original_price }}
            </span>
          </div>
          
          <div class="vip-price-row" v-if="hasVipPrice">
            <span class="label">{{ hasActiveVip ? '会员价' : 'VIP价' }}</span>
            <span class="vip-price">¥{{ product.vip_price }}</span>
            <el-tag :type="hasActiveVip ? 'success' : 'danger'" size="small" style="margin-left: 10px">
              {{ hasActiveVip ? '已生效' : '会员专享' }}
            </el-tag>
          </div>
        </div>
        
        <div class="info-row">
          <span class="label">销量</span>
          <span>{{ product.sold_count || 0 }} 件</span>
        </div>
        
        <div class="info-row">
          <span class="label">库存</span>
          <span :class="{ 'low-stock': product.available_stock < 10 }">
            {{ product.available_stock }} 件
            <el-tag v-if="product.available_stock < 10" type="warning" size="small">库存紧张</el-tag>
          </span>
        </div>
        
        <div class="quantity-section">
          <span class="label">数量</span>
          <el-input-number
            v-model="quantity"
            :min="1"
            :max="product.available_stock"
            size="large"
          />
        </div>
        
        <div class="action-buttons">
          <el-button
            type="primary"
            size="large"
            :disabled="product.available_stock === 0 || product.status !== 1"
            @click="addToCart"
          >
            <el-icon><ShoppingCartFull /></el-icon>
            {{ product.status === 1 ? '加入购物车' : '已下架' }}
          </el-button>
          <el-button
            size="large"
            @click="buyNow"
            :disabled="product.available_stock === 0 || product.status !== 1"
          >
            立即购买
          </el-button>
          <el-button size="large" @click="goBack">
            <el-icon><Back /></el-icon>
            返回
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 商品详情和评价 -->
    <el-tabs v-model="activeTab" class="detail-tabs">
      <el-tab-pane label="商品详情" name="detail">
        <div class="detail-content" v-html="product.description || '暂无详情'"></div>
      </el-tab-pane>
      
      <el-tab-pane label="商品评价" name="reviews">
        <div class="reviews-section">
          <div class="rating-summary">
            <div class="avg-rating">
              <span class="rating-value">{{ avgRating }}</span>
              <el-rate v-model="avgRating" disabled show-score text-color="#ff9900" />
              <span class="review-count">{{ reviewTotal }} 条评价</span>
            </div>
          </div>
          
          <div class="review-list">
            <div v-for="review in reviews" :key="review.review_id" class="review-item">
              <div class="review-header">
                <div class="user-info">
                  <el-avatar :size="40">{{ review.user_id }}</el-avatar>
                  <span class="username">{{ review.is_anonymous ? '匿名用户' : `用户${review.user_id}` }}</span>
                </div>
                <el-rate v-model="review.rating" disabled />
              </div>
              <div class="review-content">
                <p>{{ review.comment }}</p>
                <div class="review-images" v-if="review.images">
                  <el-image
                    v-for="(img, idx) in review.images.split(',')"
                    :key="idx"
                    :src="img"
                    :preview-src-list="review.images.split(',')"
                    fit="cover"
                    style="width: 100px; height: 100px; margin-right: 10px"
                  />
                </div>
              </div>
              <div class="review-footer">
                <span class="time">{{ formatDate(review.create_time) }}</span>
              </div>
            </div>
            
            <el-empty v-if="reviews.length === 0" description="暂无评价" />
          </div>
          
          <div class="pagination-wrapper" v-if="reviewTotal > 0">
            <el-pagination
              v-model:current-page="reviewPage"
              :page-size="10"
              :total="reviewTotal"
              layout="prev, pager, next"
              @current-change="loadReviews"
            />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'
import { getToken } from '@/utils/auth'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const product = ref({})
const quantity = ref(1)
const activeTab = ref('detail')

const defaultImage = 'https://via.placeholder.com/400x400?text=Product'

// 评价相关
const reviews = ref([])
const reviewPage = ref(1)
const reviewTotal = ref(0)

const avgRating = computed(() => {
  if (reviews.value.length === 0) return 5
  const sum = reviews.value.reduce((acc, r) => acc + r.rating, 0)
  return (sum / reviews.value.length).toFixed(1)
})

const subImages = computed(() => {
  if (!product.value.sub_images) return []
  try {
    return JSON.parse(product.value.sub_images)
  } catch {
    return product.value.sub_images.split(',')
  }
})

const hasActiveVip = computed(() => {
  const user = userStore.user
  if (!user?.vip_active) return false
  if (!user.vip_expire_time) return true
  return new Date(user.vip_expire_time).getTime() > Date.now()
})

const hasVipPrice = computed(() => {
  const vipPrice = Number(product.value.vip_price || 0)
  const price = Number(product.value.price || 0)
  return vipPrice > 0 && vipPrice < price
})

const displayPrice = computed(() => {
  if (hasActiveVip.value && hasVipPrice.value) {
    return product.value.vip_price
  }
  return product.value.price
})

const loadProduct = async () => {
  loading.value = true
  try {
    product.value = await api.product.getDetail(route.params.id)
  } catch (error) {
    console.error('加载商品详情失败:', error)
    ElMessage.error('商品不存在')
    router.back()
  } finally {
    loading.value = false
  }
}

const hydrateUser = async () => {
  if (getToken() && !userStore.hasUser) {
    await userStore.ensureSession()
  }
}

const loadReviews = async () => {
  try {
    const data = await api.review.getProductReviews(route.params.id, {
      page: reviewPage.value,
      per_page: 10
    })
    reviews.value = data.items || []
    reviewTotal.value = data.total || 0
  } catch (error) {
    console.error('加载评价失败:', error)
  }
}

const addToCart = async () => {
  if (!getToken()) {
    ElMessage.warning('请先登录')
    router.push('/login?redirect=' + route.fullPath)
    return
  }
  
  try {
    await api.cart.add({
      product_id: product.value.product_id,
      quantity: quantity.value
    })
    ElMessage.success('已加入购物车')
  } catch (error) {
    console.error('加入购物车失败:', error)
  }
}

const buyNow = () => {
  if (!getToken()) {
    ElMessage.warning('请先登录')
    router.push('/login?redirect=' + route.fullPath)
    return
  }
  
  // 先加入购物车,再跳转到购物车页
  addToCart().then(() => {
    router.push('/cart')
  })
}

const goBack = () => {
  router.back()
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  hydrateUser()
  loadProduct()
  loadReviews()
})
</script>

<style lang="scss" scoped>
.product-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.product-main {
  display: flex;
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.product-gallery {
  width: 450px;
  margin-right: 40px;
  
  .main-image {
    width: 100%;
    height: 450px;
    border: 1px solid #eee;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 15px;
  }
  
  .thumbnail-list {
    display: flex;
    gap: 10px;
    
    .thumbnail-item {
      width: 80px;
      height: 80px;
      border: 1px solid #eee;
      border-radius: 4px;
      overflow: hidden;
      cursor: pointer;
      
      &:hover {
        border-color: #ff6700;
      }
    }
  }
}

.product-info {
  flex: 1;
  
  .product-title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 15px;
    line-height: 1.4;
  }
  
  .product-subtitle {
    color: #999;
    margin-bottom: 20px;
    font-size: 14px;
    line-height: 1.6;
  }
  
  .price-section {
    background: #fff8f0;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    
    .price-row {
      display: flex;
      align-items: center;
      margin-bottom: 10px;
      
      .label {
        width: 60px;
        color: #999;
      }
      
      .current-price {
        font-size: 28px;
        font-weight: bold;
        color: #ff6700;
      }
      
      .original-price {
        font-size: 16px;
        color: #999;
        text-decoration: line-through;
        margin-left: 15px;
      }
    }
    
    .vip-price-row {
      display: flex;
      align-items: center;
      
      .label {
        width: 60px;
        color: #999;
      }
      
      .vip-price {
        font-size: 22px;
        font-weight: bold;
        color: #ff6700;
      }
    }
  }
  
  .info-row {
    display: flex;
    align-items: center;
    padding: 15px 0;
    border-bottom: 1px solid #f0f0f0;
    
    .label {
      width: 60px;
      color: #999;
    }
    
    .low-stock {
      color: #f56c6c;
    }
  }
  
  .quantity-section {
    display: flex;
    align-items: center;
    padding: 20px 0;
    
    .label {
      width: 60px;
      color: #999;
    }
  }
  
  .action-buttons {
    display: flex;
    gap: 15px;
    margin-top: 20px;
    
    .el-button--primary {
      background-color: #ff6700;
      border-color: #ff6700;
      flex: 1;
      
      &:hover {
        background-color: #ff8533;
        border-color: #ff8533;
      }
    }
  }
}

.detail-tabs {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  
  .detail-content {
    padding: 20px;
    line-height: 1.8;
    color: #666;
  }
}

.reviews-section {
  .rating-summary {
    padding: 20px;
    background: #f9f9f9;
    border-radius: 8px;
    margin-bottom: 20px;
    
    .avg-rating {
      display: flex;
      align-items: center;
      
      .rating-value {
        font-size: 48px;
        font-weight: bold;
        color: #ff6700;
        margin-right: 15px;
      }
      
      .review-count {
        margin-left: 15px;
        color: #999;
      }
    }
  }
  
  .review-list {
    .review-item {
      padding: 20px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
    }
    
    .review-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
      
      .user-info {
        display: flex;
        align-items: center;
        
        .username {
          margin-left: 10px;
          font-weight: 500;
        }
      }
    }
    
    .review-content {
      p {
        line-height: 1.8;
        color: #666;
        margin-bottom: 15px;
      }
      
      .review-images {
        display: flex;
        flex-wrap: wrap;
      }
    }
    
    .review-footer {
      margin-top: 10px;
      
      .time {
        font-size: 12px;
        color: #999;
      }
    }
  }
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
