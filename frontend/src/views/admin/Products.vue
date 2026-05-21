<template>
  <div class="admin-products">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>商品管理</span>
          <div>
            <el-input
              v-model="keyword"
              placeholder="搜索商品"
              style="width: 250px; margin-right: 10px"
              clearable
              @keyup.enter="handleSearch"
            />
            <el-button type="primary" @click="handleAdd">添加商品</el-button>
          </div>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="product_id" label="ID" width="80" />
        <el-table-column label="商品图片" width="80">
          <template #default="{ row }">
            <el-image v-if="row.main_image" :src="row.main_image" fit="cover" class="table-product-image">
              <template #error>
                <div class="table-product-image product-image-fallback">加载失败</div>
              </template>
            </el-image>
            <div v-else class="table-product-image product-image-fallback">无图</div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="商品名称" min-width="180" />
        <el-table-column label="分类" width="100">
          <template #default="{ row }">
            {{ categoryNameMap[row.category_id] || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="标签" width="140">
          <template #default="{ row }">
            <el-tag v-if="row.is_hot" size="small" type="danger" style="margin-right: 4px">热销</el-tag>
            <el-tag v-if="row.is_new" size="small" type="success" style="margin-right: 4px">新品</el-tag>
            <el-tag v-if="row.is_recommend" size="small" type="warning">推荐</el-tag>
            <span v-if="!row.is_hot && !row.is_new && !row.is_recommend">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="original_price" label="原价" width="100">
          <template #default="{ row }">
            <span v-if="row.original_price">¥{{ row.original_price }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="vip_price" label="会员价" width="100">
          <template #default="{ row }">
            <span v-if="row.vip_price !== null && row.vip_price !== undefined">¥{{ row.vip_price }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="exchange_points" label="兑换积分" width="100" />
        <el-table-column prop="stock" label="库存" width="70" />
        <el-table-column prop="sold_count" label="销量" width="70" />
        <el-table-column label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="310" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="primary" @click="openSkuDialog(row)">规格</el-button>
            <el-button
              v-if="row.status === 1"
              size="small"
              type="warning"
              @click="handleOffShelf(row)"
            >
              下架
            </el-button>
            <el-button
              v-else
              size="small"
              type="success"
              @click="handleOnShelf(row)"
            >
              上架
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

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

    <!-- 商品编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="商品名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="商品分类">
          <div style="display: flex; gap: 8px; width: 100%">
            <el-tree-select
              v-model="form.category_id"
              :data="categoryTree"
              :props="{ label: 'name', value: 'category_id', children: 'children' }"
              placeholder="请选择分类"
              check-strictly
              clearable
              filterable
              style="flex: 1"
            />
            <el-button @click="openCategoryDialog">新增分类</el-button>
          </div>
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="form.price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item v-if="isEdit" label="原价">
          <el-input-number v-model="form.original_price" :min="0" :precision="2" />
          <span class="form-tip">修改价格时留空则自动填充上次价格</span>
        </el-form-item>
        <el-form-item label="会员价">
          <el-input-number v-model="form.vip_price" :min="0" :precision="2" />
          <span class="form-tip">0 表示不启用会员价</span>
        </el-form-item>
        <el-form-item label="库存">
          <el-input-number v-model="form.stock" :min="0" />
        </el-form-item>
        <el-form-item label="兑换积分">
          <el-input-number v-model="form.exchange_points" :min="0" :step="100" style="width: 200px" />
          <span class="form-tip">0 表示不可兑换</span>
        </el-form-item>
        <el-form-item label="品牌">
          <el-input v-model="form.brand" />
        </el-form-item>
        <el-form-item label="商品主图">
          <div class="product-image-field">
            <el-upload
              action="#"
              :show-file-list="false"
              :before-upload="beforeProductImageUpload"
              :http-request="uploadProductImage"
              accept="image/png,image/jpeg,image/gif,image/webp"
            >
              <div class="product-image-uploader" :class="{ 'is-loading': productImageUploading }">
                <el-image v-if="form.main_image" :src="form.main_image" fit="cover" class="product-image-preview">
                  <template #error>
                    <div class="product-image-placeholder">图片加载失败</div>
                  </template>
                </el-image>
                <div v-else class="product-image-placeholder">
                  {{ productImageUploading ? '上传中' : '上传主图' }}
                </div>
              </div>
            </el-upload>
            <div class="product-image-actions">
              <el-input
                v-model="form.main_image"
                placeholder="上传后自动填入，也可粘贴图片 URL"
                clearable
              />
              <el-button v-if="form.main_image" @click="form.main_image = ''">清除</el-button>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="商品标签">
          <el-checkbox v-model="form.is_hot" :true-value="1" :false-value="0">热销</el-checkbox>
          <el-checkbox v-model="form.is_new" :true-value="1" :false-value="0">新品</el-checkbox>
          <el-checkbox v-model="form.is_recommend" :true-value="1" :false-value="0">推荐</el-checkbox>
        </el-form-item>
        <el-form-item label="自定义标签">
          <el-select
            v-model="formTagIds"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入标签名创建"
            style="width: 100%"
            @change="onTagSelectChange"
          >
            <el-option
              v-for="tag in allTags"
              :key="tag.tag_id"
              :label="tag.name"
              :value="tag.tag_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新建分类对话框 -->
    <el-dialog v-model="categoryDialogVisible" title="新增分类" width="450px">
      <el-form :model="newCategoryForm" label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="newCategoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="父级分类">
          <el-tree-select
            v-model="newCategoryForm.parent_id"
            :data="categoryTree"
            :props="{ label: 'name', value: 'category_id', children: 'children' }"
            placeholder="不选则为一级分类"
            check-strictly
            clearable
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createCategory">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- SKU 规格管理对话框 -->
    <el-dialog v-model="skuDialogVisible" title="规格管理" width="800px" @opened="initSkuDialog">
      <div v-if="skuProductId">
        <!-- 规格模板选择区 -->
        <el-card shadow="never" style="margin-bottom: 16px">
          <template #header><span style="font-weight: 600">选择规格模板</span></template>
          <div style="display: flex; flex-wrap: wrap; gap: 16px">
            <div v-for="tpl in specTemplates" :key="tpl.template_id" style="display: flex; align-items: center; gap: 8px">
              <el-checkbox
                :model-value="selectedTemplateIds.includes(tpl.template_id)"
                @change="(val) => toggleTemplate(tpl.template_id, val)"
              >
                {{ tpl.name }}
              </el-checkbox>
              <el-select
                v-if="selectedTemplateIds.includes(tpl.template_id)"
                v-model="selectedSpecValues[tpl.template_id]"
                multiple
                placeholder="选择规格值"
                size="small"
                style="width: 200px"
              >
                <el-option
                  v-for="sv in tpl.values"
                  :key="sv.value_id"
                  :label="sv.value"
                  :value="sv.value_id"
                />
              </el-select>
            </div>
          </div>
          <el-button
            v-if="selectedTemplateIds.length > 0"
            type="primary"
            size="small"
            style="margin-top: 12px"
            @click="generateSkuCombinations"
          >
            生成规格组合
          </el-button>
        </el-card>

        <!-- SKU 列表 -->
        <el-card v-if="skuRows.length > 0" shadow="never">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span style="font-weight: 600">SKU 列表（{{ skuRows.length }} 条）</span>
              <div style="display: flex; gap: 8px">
                <el-input-number
                  v-model="batchPrice"
                  :min="0"
                  :precision="2"
                  placeholder="批量价格"
                  size="small"
                  style="width: 130px"
                />
                <el-button size="small" @click="applyBatchPrice">应用价格</el-button>
                <el-input-number
                  v-model="batchStock"
                  :min="0"
                  placeholder="批量库存"
                  size="small"
                  style="width: 130px"
                />
                <el-button size="small" @click="applyBatchStock">应用库存</el-button>
              </div>
            </div>
          </template>
          <el-table :data="skuRows" size="small" max-height="400">
            <el-table-column label="规格" min-width="200">
              <template #default="{ row }">{{ row.spec_text }}</template>
            </el-table-column>
            <el-table-column label="价格" width="150">
              <template #default="{ row }">
                <el-input-number v-model="row.price" :min="0" :precision="2" size="small" style="width: 130px" />
              </template>
            </el-table-column>
            <el-table-column label="库存" width="130">
              <template #default="{ row }">
                <el-input-number v-model="row.stock" :min="0" size="small" style="width: 110px" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="60">
              <template #default="{ $index }">
                <el-button size="small" type="danger" text @click="skuRows.splice($index, 1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
      <template #footer>
        <el-button @click="skuDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSkus" :loading="skuSaving">保存规格</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'

const loading = ref(false)
const tableData = ref([])
const page = ref(1)
const perPage = ref(20)
const total = ref(0)
const keyword = ref('')
const categoryTree = ref([])
const categoryNameMap = ref({})

// ---- 商品编辑 ----
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)
const form = ref({
  name: '',
  category_id: null,
  price: 0,
  original_price: null,
  vip_price: null,
  stock: 0,
  exchange_points: 0,
  brand: '',
  main_image: '',
  is_hot: 0,
  is_new: 0,
  is_recommend: 0,
  description: ''
})

const dialogTitle = computed(() => isEdit.value ? '编辑商品' : '添加商品')

// ---- 分类管理 ----
const categoryDialogVisible = ref(false)
const newCategoryForm = ref({ name: '', parent_id: null })

// ---- SKU 管理 ----
const skuDialogVisible = ref(false)
const skuProductId = ref(null)
const skuSaving = ref(false)
const specTemplates = ref([])
const selectedTemplateIds = ref([])
const selectedSpecValues = ref({})
const skuRows = ref([])
const batchPrice = ref(null)
const batchStock = ref(null)

// ---- 标签管理 ----
const allTags = ref([])
const formTagIds = ref([])
const tagNameCache = ref({})
const productImageUploading = ref(false)

// ==================== 分类 ====================

const buildCategoryMap = (tree) => {
  for (const node of tree) {
    categoryNameMap.value[node.category_id] = node.name
    if (node.children && node.children.length > 0) {
      buildCategoryMap(node.children)
    }
  }
}

const loadCategories = async () => {
  try {
    const res = await api.category.getList()
    categoryTree.value = res || []
    categoryNameMap.value = {}
    buildCategoryMap(res || [])
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

const openCategoryDialog = () => {
  newCategoryForm.value = { name: '', parent_id: null }
  categoryDialogVisible.value = true
}

const createCategory = async () => {
  const name = (newCategoryForm.value.name || '').trim()
  if (!name) { ElMessage.warning('请输入分类名称'); return }
  try {
    await api.admin.createCategory({
      name,
      parent_id: newCategoryForm.value.parent_id || 0
    })
    ElMessage.success('分类创建成功')
    categoryDialogVisible.value = false
    await loadCategories()
  } catch (error) { /* error handled by interceptor */ }
}

// ==================== 标签 ====================

const loadTags = async () => {
  try {
    const res = await api.admin.getTags()
    allTags.value = res || []
    tagNameCache.value = {}
    for (const t of allTags.value) {
      tagNameCache.value[t.tag_id] = t.name
    }
  } catch (error) { console.error('加载标签失败:', error) }
}

const loadProductTags = async (productId) => {
  if (!allTags.value.length) await loadTags()
  try {
    const tags = await api.product.getProductTags(productId)
    // 确保产品已有标签都在 allTags 中
    for (const t of (tags || [])) {
      if (!tagNameCache.value[t.tag_id]) {
        allTags.value.push({ tag_id: t.tag_id, name: t.name })
        tagNameCache.value[t.tag_id] = t.name
      }
    }
    formTagIds.value = (tags || []).map(t => t.tag_id)
  } catch { formTagIds.value = [] }
}

const onTagSelectChange = async (vals) => {
  // vals is an array of tag_ids (numbers) and possibly string names (from allow-create)
  for (let i = 0; i < vals.length; i++) {
    const val = vals[i]
    if (typeof val === 'string') {
      try {
        const newTag = await api.admin.createTag({ name: val.trim() })
        vals[i] = newTag.tag_id
        allTags.value.push(newTag)
        tagNameCache.value[newTag.tag_id] = newTag.name
      } catch { /* skip if already exists */ }
    }
  }
  formTagIds.value = vals.filter(v => typeof v !== 'string')
}

const saveProductTags = async (productId) => {
  try {
    await api.product.setProductTags(productId, { tag_ids: formTagIds.value })
  } catch (error) { console.error('保存标签失败:', error) }
}

// ==================== 商品 ====================

const loadProducts = async () => {
  loading.value = true
  try {
    const res = await api.admin.getProducts({ page: page.value, per_page: perPage.value, keyword: keyword.value })
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载商品失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { page.value = 1; loadProducts() }

const handleAdd = () => {
  isEdit.value = false
  currentId.value = null
  form.value = {
    name: '', category_id: null, price: 0, original_price: null,
    vip_price: null, stock: 0, exchange_points: 0, brand: '',
    main_image: '', is_hot: 0, is_new: 0, is_recommend: 0, description: ''
  }
  formTagIds.value = []
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.product_id
  form.value = {
    name: row.name || '',
    category_id: row.category_id || null,
    price: row.price || 0,
    original_price: row.original_price || null,
    vip_price: row.vip_price !== null && row.vip_price !== undefined ? row.vip_price : null,
    stock: row.stock || 0,
    exchange_points: row.exchange_points || 0,
    brand: row.brand || '',
    main_image: row.main_image || '',
    is_hot: row.is_hot || 0,
    is_new: row.is_new || 0,
    is_recommend: row.is_recommend || 0,
    description: row.description || ''
  }
  loadProductTags(row.product_id)
  dialogVisible.value = true
}

const handleOffShelf = async (row) => {
  try {
    await ElMessageBox.confirm(
      `下架商品"${row.name}"将自动取消所有包含该商品的未完成订单（已支付订单将退款）。确定继续吗？`,
      '警告', { type: 'warning' }
    )
    await api.admin.offShelfProduct(row.product_id)
    ElMessage.success('商品已下架')
    loadProducts()
  } catch (error) {
    if (error !== 'cancel') console.error('下架失败:', error)
  }
}

const handleOnShelf = async (row) => {
  try {
    await api.admin.updateProduct(row.product_id, { status: 1 })
    ElMessage.success('商品已上架')
    loadProducts()
  } catch (error) { console.error('上架失败:', error) }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `永久删除商品"${row.name}"将无法恢复。如果该商品已有订单记录，则无法删除。确定继续吗？`,
      '警告', { type: 'error' }
    )
    await api.admin.deleteProductPermanently(row.product_id)
    ElMessage.success('商品已永久删除')
    loadProducts()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

const beforeProductImageUpload = (file) => {
  const allowedTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.warning('仅支持 png/jpg/jpeg/gif/webp')
    return false
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.warning('图片大小不能超过 5MB')
    return false
  }
  return true
}

const uploadProductImage = async ({ file, onSuccess, onError }) => {
  productImageUploading.value = true
  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await api.admin.uploadProductImage(formData)
    form.value.main_image = res.url
    ElMessage.success('图片上传成功')
    onSuccess && onSuccess(res)
  } catch (error) {
    onError && onError(error)
  } finally {
    productImageUploading.value = false
  }
}

const submitForm = async () => {
  try {
    const payload = { ...form.value }
    if (!isEdit.value) {
      delete payload.original_price
    }
    if (payload.vip_price === null) {
      payload.vip_price = 0
    }
    let savedProductId = currentId.value
    if (isEdit.value) {
      await api.admin.updateProduct(currentId.value, payload)
      ElMessage.success('更新成功')
    } else {
      const res = await api.admin.createProduct(payload)
      ElMessage.success('添加成功')
      savedProductId = res?.product_id || null
    }
    // 保存标签
    if (savedProductId) {
      await saveProductTags(savedProductId)
    }
    dialogVisible.value = false
    loadProducts()
    // 新建成功后询问是否配置规格
    if (!isEdit.value && savedProductId) {
      try {
        await ElMessageBox.confirm('商品已创建，是否立即配置商品规格（SKU）？', '提示', {
          confirmButtonText: '去配置', cancelButtonText: '稍后', type: 'info'
        })
        openSkuDialog({ product_id: savedProductId })
      } catch { /* 用户选择稍后 */ }
    }
  } catch (error) { console.error('提交失败:', error) }
}

// ==================== SKU 规格管理 ====================

const loadSpecTemplates = async () => {
  try {
    const res = await api.product.getSpecTemplates()
    specTemplates.value = res || []
  } catch (error) { console.error('加载规格模板失败:', error) }
}

const openSkuDialog = async (row) => {
  skuProductId.value = row.product_id
  skuDialogVisible.value = true
}

const initSkuDialog = async () => {
  selectedTemplateIds.value = []
  selectedSpecValues.value = {}
  skuRows.value = []
  batchPrice.value = null
  batchStock.value = null

  await loadSpecTemplates()

  // 加载已有 SKU
  if (skuProductId.value) {
    try {
      const product = await api.product.getDetail(skuProductId.value)
      if (product && product.skus && product.skus.length > 0) {
        // 从已有 SKU 恢复规格选择
        const allSpecIds = new Set()
        for (const sku of product.skus) {
          let ids = sku.spec_ids
          if (typeof ids === 'string') {
            try { ids = JSON.parse(ids) } catch { ids = [] }
          }
          if (Array.isArray(ids)) {
            ids.forEach(id => allSpecIds.add(id))
          }
        }
        // 找出涉及哪些模板
        for (const tpl of specTemplates.value) {
          const tplValueIds = new Set(tpl.values.map(v => v.value_id))
          const matched = [...allSpecIds].filter(id => tplValueIds.has(id))
          if (matched.length > 0) {
            selectedTemplateIds.value.push(tpl.template_id)
            selectedSpecValues.value[tpl.template_id] = matched
          }
        }
        // 恢复 SKU 行
        skuRows.value = product.skus.map(sku => {
          let ids = sku.spec_ids
          if (typeof ids === 'string') {
            try { ids = JSON.parse(ids) } catch { ids = [] }
          }
          return {
            spec_ids: Array.isArray(ids) ? ids : [],
            spec_text: sku.spec_text || '',
            price: sku.price || 0,
            stock: sku.stock || 0
          }
        })
      }
    } catch (error) { console.error('加载商品 SKU 失败:', error) }
  }
}

const toggleTemplate = (templateId, checked) => {
  if (checked) {
    if (!selectedTemplateIds.value.includes(templateId)) {
      selectedTemplateIds.value.push(templateId)
    }
    if (!selectedSpecValues.value[templateId]) {
      selectedSpecValues.value[templateId] = []
    }
  } else {
    selectedTemplateIds.value = selectedTemplateIds.value.filter(id => id !== templateId)
    delete selectedSpecValues.value[templateId]
  }
}

const generateSkuCombinations = () => {
  // 为每个选中的模板收集选中的规格值
  const valueArrays = []
  for (const tid of selectedTemplateIds.value) {
    const tpl = specTemplates.value.find(t => t.template_id === tid)
    if (!tpl) continue
    const selectedIds = selectedSpecValues.value[tid] || []
    if (selectedIds.length === 0) continue
    const values = selectedIds.map(vid => {
      const sv = tpl.values.find(v => v.value_id === vid)
      return { template_name: tpl.name, value_name: sv ? sv.value : '', value_id: vid }
    })
    valueArrays.push(values)
  }

  if (valueArrays.length === 0) {
    ElMessage.warning('请至少选择一个规格值')
    return
  }

  // 笛卡尔积
  const cartesian = (arrays) => {
    if (arrays.length === 0) return [[]]
    const [first, ...rest] = arrays
    const restProduct = cartesian(rest)
    const result = []
    for (const item of first) {
      for (const combo of restProduct) {
        result.push([item, ...combo])
      }
    }
    return result
  }

  const combinations = cartesian(valueArrays)

  // 保留旧 SKU 中已有的价格库存（按 spec_ids 匹配）
  const oldMap = new Map()
  for (const row of skuRows.value) {
    const key = JSON.stringify([...row.spec_ids].sort())
    oldMap.set(key, { price: row.price, stock: row.stock })
  }

  skuRows.value = combinations.map(combo => {
    const spec_ids = combo.map(c => c.value_id)
    const spec_text = combo.map(c => `${c.template_name}:${c.value_name}`).join(' / ')
    const key = JSON.stringify([...spec_ids].sort())
    const old = oldMap.get(key)
    return {
      spec_ids,
      spec_text,
      price: old ? old.price : (form.value.price || 0),
      stock: old ? old.stock : 0
    }
  })
}

const applyBatchPrice = () => {
  if (batchPrice.value !== null && batchPrice.value !== undefined) {
    for (const row of skuRows.value) {
      row.price = batchPrice.value
    }
  }
}

const applyBatchStock = () => {
  if (batchStock.value !== null && batchStock.value !== undefined) {
    for (const row of skuRows.value) {
      row.stock = batchStock.value
    }
  }
}

const saveSkus = async () => {
  skuSaving.value = true
  try {
    await api.product.saveProductSkus(skuProductId.value, {
      skus: skuRows.value.map(row => ({
        spec_ids: row.spec_ids,
        price: row.price,
        stock: row.stock
      }))
    })
    ElMessage.success('规格保存成功')
    skuDialogVisible.value = false
    loadProducts()
  } catch (error) { console.error('保存规格失败:', error) }
  finally { skuSaving.value = false }
}

// ==================== Init ====================

onMounted(() => {
  loadCategories()
  loadTags()
  loadProducts()
})
</script>

<style scoped>
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.table-product-image {
  width: 50px;
  height: 50px;
  border-radius: 6px;
}

.product-image-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #909399;
  font-size: 12px;
  border: 1px dashed #dcdfe6;
}

.product-image-field {
  width: 100%;
  display: flex;
  gap: 12px;
  align-items: center;
}

.product-image-uploader {
  width: 96px;
  height: 96px;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  background: #fafafa;
  transition: border-color 0.2s;
}

.product-image-uploader:hover {
  border-color: #409eff;
}

.product-image-uploader.is-loading {
  opacity: 0.65;
  pointer-events: none;
}

.product-image-preview,
.product-image-placeholder {
  width: 96px;
  height: 96px;
}

.product-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 13px;
}

.product-image-actions {
  flex: 1;
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>
