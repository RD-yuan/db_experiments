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
            <span class="current-price">¥{{ currentSku && currentSku.price !== null ? currentSku.price : displayPrice }}</span>
            <span class="original-price" v-if="showOriginalPrice">¥{{ skuOriginalPrice || product.price }}</span>
          </div>
          <div class="price-row vip-row" v-if="hasVipPrice">
            <span class="label">VIP专享价</span>
            <span class="vip-price">¥{{ skuVipPrice }}</span>
            <el-tag v-if="hasActiveVip" type="success" size="small" style="margin-left: 8px">已生效</el-tag>
            <el-tag v-else type="danger" size="small" style="margin-left: 8px">会员专享</el-tag>
          </div>
          <div class="vip-discount-tip" v-if="hasActiveVip">
            <el-tag type="warning" size="small">
              {{ discountText }}，到手价 ¥{{ finalPrice }}
            </el-tag>
          </div>
        </div>

        <div class="info-row">
          <span class="label">销量</span>
          <span>{{ product.sold_count || 0 }} 件</span>
        </div>

        <div class="info-row">
          <span class="label">库存</span>
          <span :class="{ 'low-stock': (currentSku ? currentSku.available_stock : product.available_stock) < 10 }">
            {{ currentSku ? currentSku.available_stock : product.available_stock }} 件
            <el-tag v-if="(currentSku ? currentSku.available_stock : product.available_stock) < 10" type="warning" size="small">库存紧张</el-tag>
          </span>
        </div>

        <div class="sku-section" v-if="product.has_sku && product.skus && product.skus.length > 0">
          <div v-for="tpl in skuTemplates" :key="tpl.template_id" class="sku-group">
            <span class="label">{{ tpl.name }}</span>
            <div class="sku-options">
              <el-button
                v-for="val in tpl.values"
                :key="val.value_id"
                :type="selectedSpecs[tpl.template_id] === val.value_id ? 'primary' : 'default'"
                size="small"
                @click="selectSpec(tpl.template_id, val.value_id)"
              >{{ val.value }}</el-button>
            </div>
          </div>
        </div>

        <div class="quantity-section">
          <span class="label">数量</span>
          <el-input-number
            v-model="quantity"
            :min="1"
            :max="currentSku ? currentSku.available_stock : product.available_stock"
            size="large"
          />
        </div>

        <div class="action-buttons">
          <el-button
            type="primary"
            size="large"
            :disabled="(currentSku ? currentSku.available_stock : product.available_stock) === 0 || product.status !== 1"
            @click="addToCart"
          >
            <el-icon><ShoppingCartFull /></el-icon>
            {{ product.status === 1 ? '加入购物车' : '已下架' }}
          </el-button>
          <el-button
            size="large"
            @click="buyNow"
            :disabled="(currentSku ? currentSku.available_stock : product.available_stock) === 0 || product.status !== 1"
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
              <span class="rating-value">{{ reviewTotal > 0 ? avgRating : '-' }}</span>
              <el-rate v-if="reviewTotal > 0" v-model="avgRating" disabled show-score text-color="#ff9900" />
              <span class="review-count">{{ reviewTotal > 0 ? reviewTotal + ' 条评价' : '暂无评价' }}</span>
            </div>
          </div>

          <!-- 好评/差评筛选 -->
          <div class="rating-filter" v-if="reviewsLoaded">
            <el-radio-group v-model="ratingFilter" size="small" @change="onFilterChange">
              <el-radio-button value="">全部</el-radio-button>
              <el-radio-button value="good">好评</el-radio-button>
              <el-radio-button value="bad">差评</el-radio-button>
            </el-radio-group>
          </div>

          <div class="review-list">
            <div v-for="review in reviews" :key="review.review_id" class="review-item">
              <div class="review-header">
                <div class="user-info">
                  <el-avatar :size="40">{{ review.user_id }}</el-avatar>
                  <span class="username">{{ review.is_anonymous ? '匿名用户' : review.username }}</span>
                </div>
                <el-rate v-model="review.rating" disabled />
              </div>
              <div class="review-content">
                <p>{{ review.comment }}</p>
                <div class="review-images" v-if="review.images">
                  <el-image
                    v-for="(img, idx) in parseImages(review.images)"
                    :key="idx"
                    :src="img"
                    :preview-src-list="parseImages(review.images)"
                    fit="cover"
                    style="width: 100px; height: 100px; margin-right: 10px"
                  />
                </div>
              </div>
              <!-- 追评 -->
              <div v-if="review.follow_up_comment" class="follow-up">
                <div class="follow-up-tag">追评</div>
                <p>{{ review.follow_up_comment }}</p>
                <div class="review-images" v-if="review.follow_up_images">
                  <el-image
                    v-for="(img, idx) in parseImages(review.follow_up_images)"
                    :key="'fu'+idx"
                    :src="img"
                    :preview-src-list="parseImages(review.follow_up_images)"
                    fit="cover"
                    style="width: 100px; height: 100px; margin-right: 10px"
                  />
                </div>
                <span class="time" v-if="review.follow_up_time">{{ formatDate(review.follow_up_time) }}</span>
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
const selectedSpecs = ref({})
const currentSku = ref(null)
const skuTemplates = ref([])

const findMatchingSku = () => {
  if (!product.value.has_sku || !product.value.skus) return null
  const selectedIds = Object.values(selectedSpecs.value).filter(Boolean)
  if (selectedIds.length === 0) return null
  return product.value.skus.find(sku => {
    let specIds = sku.spec_ids
    if (typeof specIds === 'string') specIds = JSON.parse(specIds)
    if (selectedIds.length !== specIds.length) return false
    return selectedIds.every(id => specIds.includes(id))
  }) || null
}

const selectSpec = (templateId, valueId) => {
  selectedSpecs.value[templateId] = valueId
  currentSku.value = findMatchingSku()
}

const buildTemplatesFromSkuText = () => {
  const groups = {}
  product.value.skus.forEach(sku => {
    const text = sku.spec_text || ''
    const parts = text.split(' / ').filter(Boolean)
    parts.forEach((part, idx) => {
      const colonIdx = part.indexOf(':')
      let tplName, valName
      if (colonIdx > 0) {
        tplName = part.substring(0, colonIdx)
        valName = part.substring(colonIdx + 1)
      } else {
        tplName = '规格' + (idx + 1)
        valName = part
      }
      if (!groups[tplName]) groups[tplName] = new Set()
      groups[tplName].add(valName)
    })
  })
  let fid = 90000
  return Object.entries(groups).map(([name, values]) => ({
    template_id: fid++,
    name,
    values: [...values].map(v => ({ value_id: fid++, value: v }))
  }))
}

const loadSkuTemplates = async () => {
  if (!product.value.has_sku || !product.value.skus || !product.value.skus.length) return
  try {
    let templates = await api.product.getSpecTemplates()
    if (!templates || !templates.length) {
      templates = buildTemplatesFromSkuText()
    } else {
      const usedSpecIds = new Set()
      product.value.skus.forEach(sku => {
        let ids = sku.spec_ids
        if (typeof ids === 'string') ids = JSON.parse(ids)
        if (ids) ids.forEach(id => usedSpecIds.add(id))
      })
      templates = templates
        .map(tpl => ({
          ...tpl,
          values: tpl.values.filter(v => usedSpecIds.has(v.value_id))
        }))
        .filter(tpl => tpl.values.length > 0)
      if (!templates.length) templates = buildTemplatesFromSkuText()
    }
    skuTemplates.value = templates
  } catch (e) {
    console.error(e)
    skuTemplates.value = buildTemplatesFromSkuText()
  }
}

const activeTab = ref('detail')
const defaultImage = 'https://via.placeholder.com/400x400?text=Product'

const discountFactor = computed(() => {
  const level = userStore.user?.vip_level || 0
  const factors = { 1: 1.0, 2: 0.95, 3: 0.9 }
  return factors[level] || 1.0
})

const discountText = computed(() => {
  const level = userStore.user?.vip_level || 0
  const texts = { 1: '会员价', 2: '金卡95折', 3: '钻石卡9折' }
  return texts[level] || ''
})

const effectiveBasePrice = computed(() => {
  if (currentSku.value && currentSku.value.price !== null && currentSku.value.price !== undefined) {
    return Number(currentSku.value.price)
  }
  return Number(product.value.price || 0)
})

const finalPrice = computed(() => {
  const baseForDiscount = hasActiveVip.value && hasVipPrice.value
    ? skuVipPrice.value
    : effectiveBasePrice.value
  return (baseForDiscount * discountFactor.value).toFixed(2)
})

// 评价相关
const reviews = ref([])
const reviewPage = ref(1)
const reviewTotal = ref(0)
const ratingFilter = ref('')
const reviewsLoaded = ref(false)

const parseImages = (imgs) => {
  if (!imgs) return []
  try { return JSON.parse(imgs) } catch { return imgs.split(',') }
}

const onFilterChange = () => {
  reviewPage.value = 1
  loadReviews()
}

const avgRating = computed(() => {
  if (reviews.value.length === 0) return 0
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

const skuOriginalPrice = computed(() => {
  if (currentSku.value && currentSku.value.original_price !== null && currentSku.value.original_price !== undefined) {
    return Number(currentSku.value.original_price)
  }
  return Number(product.value.original_price || 0)
})

const showOriginalPrice = computed(() => {
  return skuOriginalPrice.value > 0 && skuOriginalPrice.value > effectiveBasePrice.value
})

const skuVipPrice = computed(() => {
  if (currentSku.value && currentSku.value.vip_price !== null && currentSku.value.vip_price !== undefined && currentSku.value.vip_price > 0) {
    return Number(currentSku.value.vip_price)
  }
  return Number(product.value.vip_price || 0)
})

const hasVipPrice = computed(() => {
  return skuVipPrice.value > 0 && skuVipPrice.value < effectiveBasePrice.value
})

const displayPrice = computed(() => {
  return effectiveBasePrice.value
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
      per_page: 10,
      rating_type: ratingFilter.value || undefined
    })
    reviews.value = data.items || []
    reviewTotal.value = data.total || 0
    reviewsLoaded.value = true
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
    const payload = {
      product_id: product.value.product_id,
      quantity: quantity.value
    }
    if (currentSku.value) {
      payload.sku_id = currentSku.value.sku_id
    }
    await api.cart.add(payload)
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
  loadProduct().then(() => loadSkuTemplates())
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

  .sku-section {
    padding: 15px 0;
    border-bottom: 1px solid #f0f0f0;
  }
  .sku-section .sku-group { display: flex; align-items: center; margin-bottom: 10px; }
  .sku-section .label { width: 60px; color: #999; flex-shrink: 0; }
  .sku-section .sku-options { display: flex; gap: 8px; flex-wrap: wrap; }

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
  .rating-filter {
    text-align: center;
    margin-bottom: 16px;
  }

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

    .follow-up {
      margin-top: 12px;
      padding: 12px;
      background: #fff8f0;
      border-radius: 6px;
      border-left: 3px solid #ff6700;

      .follow-up-tag {
        font-size: 11px;
        color: #ff6700;
        font-weight: 600;
        margin-bottom: 8px;
      }

      p {
        color: #666;
        line-height: 1.6;
      }

      .time {
        display: block;
        margin-top: 8px;
        font-size: 12px;
        color: #999;
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
