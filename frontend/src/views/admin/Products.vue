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
            <el-image :src="row.main_image" fit="cover" style="width: 50px; height: 50px" />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="商品名称" min-width="200" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80" />
        <el-table-column prop="sold_count" label="销量" width="80" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
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
              永久删除
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="商品名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="form.price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="库存">
          <el-input-number v-model="form.stock" :min="0" />
        </el-form-item>
        <el-form-item label="品牌">
          <el-input v-model="form.brand" />
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

const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)
const form = ref({
  name: '',
  price: 0,
  stock: 0,
  brand: '',
  description: ''
})

const dialogTitle = computed(() => isEdit.value ? '编辑商品' : '添加商品')

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

const handleSearch = () => {
  page.value = 1
  loadProducts()
}

const handleAdd = () => {
  isEdit.value = false
  currentId.value = null
  form.value = { name: '', price: 0, stock: 0, brand: '', description: '' }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.product_id
  form.value = { ...row }
  dialogVisible.value = true
}

const handleOffShelf = async (row) => {
  try {
    await ElMessageBox.confirm(
      `下架商品“${row.name}”将自动取消所有包含该商品的未完成订单（已支付订单将退款）。确定继续吗？`,
      '警告',
      { type: 'warning' }
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
  } catch (error) {
    console.error('上架失败:', error)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `永久删除商品“${row.name}”将无法恢复。如果该商品已有订单记录，则无法删除。确定继续吗？`,
      '警告',
      { type: 'error' }
    )
    await api.admin.deleteProductPermanently(row.product_id)
    ElMessage.success('商品已永久删除')
    loadProducts()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

const submitForm = async () => {
  try {
    if (isEdit.value) {
      await api.admin.updateProduct(currentId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await api.admin.createProduct(form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadProducts()
  } catch (error) {
    console.error('提交失败:', error)
  }
}

onMounted(loadProducts)
</script>

<style scoped>
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
