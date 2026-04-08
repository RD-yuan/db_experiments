<template>
  <div class="product-list">
    <!-- 搜索和筛选 -->
    <div class="filter-section card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="搜索商品" clearable @clear="handleSearch" @keyup.enter="handleSearch" />
        </el-form-item>
        
        <el-form-item label="分类">
          <el-cascader
            v-model="filters.categoryPath"
            :options="categories"
            :props="{ value: 'category_id', label: 'name', children: 'children' }"
            placeholder="选择分类"
            clearable
            @change="handleCategoryChange"
          />
        </el-form-item>
        
        <el-form-item label="价格">
          <el-input v-model.number="filters.minPrice" placeholder="最低" style="width: 100px" />
          <span style="margin: 0 5px">-</span>
          <el-input v-model.number="filters.maxPrice" placeholder="最高" style="width: 100px" />
        </el-form-item>
        
        <el-form-item label="排序">
          <el-select v-model="filters.sort" placeholder="排序方式" @change="handleSearch">
            <el-option label="默认" value="" />
            <el-option label="价格升序" value="price_asc" />
            <el-option label="价格降序" value="price_desc" />
            <el-option label="销量优先" value="sold_desc" />
            <el-option label="新品优先" value="new_desc" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 商品列表 -->
    <div class="product-grid" v-loading="loading">
      <div v-if="products.length === 0 && !loading" class="empty-tip">
        <el-empty description="暂无商品" />
      </div>
      
      <div
        v-for="product in products"
        :key="product.product_id"
        class="product-item"
        @click="goToDetail(product.product_id)"
      >
        <div class="product-image">
          <el-image :src="product.main_image || defaultImage" fit="cover">
            <template #error>
              <div class="image-placeholder">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
          <div v-if="product.is_hot" class="tag hot">热销</div>
          <div v-if="product.is_new" class="tag new">新品</div>
        </div>
        
        <div class="product-info">
          <h3 class="product-name text-ellipsis-2">{{ product.name }}</h3>
          <div class="product-price">
            <span class="current-price">¥{{ product.price }}</span>
            <span v-if="product.original_price && product.original_price > product.price" class="original-price">
              ¥{{ product.original_price }}
            </span>
            <span v-if="product.vip_price" class="vip-price">VIP ¥{{ product.vip_price }}</span>
          </div>
          <div class="product-meta">
            <span>销量 {{ product.sold_count }}</span>
            <span v-if="product.available_stock < 10" class="low-stock">仅剩 {{ product.available_stock }} 件</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > 0">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :page-sizes="[20, 40, 60, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadProducts"
        @current-change="loadProducts"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const products = ref([])
const categories = ref([])
const total = ref(0)

const defaultImage = 'https://via.placeholder.com/300x300?text=Product'

const pagination = reactive({
  page: 1,
  per_page: 20
})

const filters = reactive({
  keyword: '',
  categoryPath: [],
  minPrice: null,
  maxPrice: null,
  sort: ''
})

const loadCategories = async () => {
  try {
    const data = await api.category.getList()
    categories.value = data
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

const loadProducts = async () => {
  loading.value = true
  try {
    const params = {
      ...pagination,
      keyword: filters.keyword || undefined,
      category_id: filters.categoryPath.length > 0 ? filters.categoryPath[filters.categoryPath.length - 1] : undefined,
      min_price: filters.minPrice || undefined,
      max_price: filters.maxPrice || undefined
    }
    
    // 处理排序
    if (filters.sort) {
      const [field, order] = filters.sort.split('_')
      params.sort = field
      params.order = order
    }
    
    const data = await api.product.getList(params)
    products.value = data.items
    total.value = data.total
  } catch (error) {
    console.error('加载商品失败:', error)
  } finally {
    loading.value = false
  }
}

const handleCategoryChange = () => {
  pagination.page = 1
  loadProducts()
}

const handleSearch = () => {
  pagination.page = 1
  loadProducts()
}

const handleReset = () => {
  filters.keyword = ''
  filters.categoryPath = []
  filters.minPrice = null
  filters.maxPrice = null
  filters.sort = ''
  pagination.page = 1
  loadProducts()
}

const goToDetail = (productId) => {
  router.push(`/product/${productId}`)
}

onMounted(() => {
  // 从路由参数读取筛选条件
  if (route.query.category_id) {
    filters.categoryPath = [parseInt(route.query.category_id)]
  }
  if (route.query.keyword) {
    filters.keyword = route.query.keyword
  }
  
  loadCategories()
  loadProducts()
})
</script>

<style lang="scss" scoped>
.product-list {
  padding: 20px 0;
}

.filter-section {
  :deep(.el-form-item) {
    margin-bottom: 10px;
  }
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  min-height: 400px;
}

.product-item {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  }
}

.product-image {
  position: relative;
  width: 100%;
  padding-top: 100%;
  
  .el-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
  
  .image-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f5f5;
    color: #ccc;
    font-size: 60px;
  }
  
  .tag {
    position: absolute;
    top: 10px;
    left: 10px;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    color: #fff;
    
    &.hot {
      background: #ff6700;
    }
    
    &.new {
      background: #67c23a;
    }
  }
}

.product-info {
  padding: 15px;
  
  .product-name {
    font-size: 14px;
    color: #333;
    line-height: 1.5;
    height: 42px;
    margin-bottom: 10px;
  }
  
  .product-price {
    margin-bottom: 8px;
    
    .current-price {
      font-size: 18px;
      font-weight: bold;
      color: #ff6700;
    }
    
    .original-price {
      font-size: 12px;
      color: #999;
      text-decoration: line-through;
      margin-left: 8px;
    }
    
    .vip-price {
      font-size: 12px;
      color: #ff6700;
      margin-left: 8px;
      padding: 2px 6px;
      border: 1px solid #ff6700;
      border-radius: 4px;
    }
  }
  
  .product-meta {
    font-size: 12px;
    color: #999;
    display: flex;
    justify-content: space-between;
    
    .low-stock {
      color: #f56c6c;
    }
  }
}

.empty-tip {
  grid-column: 1 / -1;
  padding: 100px 0;
}

.pagination-wrapper {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}
</style>
