<template>
  <div class="admin-coupons">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>优惠券管理</span>
          <el-button type="primary" @click="handleAdd">创建优惠券</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="coupon_id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            {{ row.type === 1 ? '满减券' : row.type === 2 ? '折扣券' : '代金券' }}
          </template>
        </el-table-column>
        <el-table-column label="优惠值" width="120">
          <template #default="{ row }">
            {{ row.type === 2 ? (row.value * 10).toFixed(1) + '折' : '¥' + row.value }}
          </template>
        </el-table-column>
        <el-table-column prop="min_order_amount" label="最低消费" width="120">
          <template #default="{ row }">¥{{ row.min_order_amount || 0 }}</template>
        </el-table-column>
        <el-table-column prop="received_count" label="已领取" width="80" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="有效期" width="200">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }} ~ {{ formatTime(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          :page-size="perPage"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadCoupons"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type">
            <el-option label="满减券" :value="1" />
            <el-option label="折扣券" :value="2" />
            <el-option label="代金券" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="优惠值">
          <el-input-number v-model="form.value" :min="0" :precision="2" />
          <span style="margin-left: 8px; color: #999">{{ form.type === 2 ? '折扣率(0.9=9折)' : '金额(元)' }}</span>
        </el-form-item>
        <el-form-item label="最低消费">
          <el-input-number v-model="form.min_order_amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="发放总数">
          <el-input-number v-model="form.total_quantity" :min="1" />
        </el-form-item>
        <el-form-item label="生效时间">
          <el-date-picker v-model="form.start_time" type="datetime" placeholder="选择开始时间" />
        </el-form-item>
        <el-form-item label="失效时间">
          <el-date-picker v-model="form.end_time" type="datetime" placeholder="选择结束时间" />
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
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const page = ref(1)
const perPage = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)
const form = ref({
  name: '',
  type: 1,
  value: 10,
  min_order_amount: 0,
  total_quantity: 100,
  start_time: null,
  end_time: null
})

const dialogTitle = computed(() => isEdit.value ? '编辑优惠券' : '创建优惠券')

const formatTime = (t) => {
  if (!t) return '-'
  return dayjs(t).format('YYYY-MM-DD HH:mm')
}

const loadCoupons = async () => {
  loading.value = true
  try {
    const res = await api.admin.getCoupons({ page: page.value, per_page: perPage.value })
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载优惠券失败:', error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  currentId.value = null
  form.value = {
    name: '',
    type: 1,
    value: 10,
    min_order_amount: 0,
    total_quantity: 100,
    start_time: null,
    end_time: null
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.coupon_id
  form.value = {
    name: row.name || '',
    type: row.type,
    value: row.value,
    min_order_amount: row.min_order_amount || 0,
    total_quantity: row.total_quantity,
    start_time: row.start_time,
    end_time: row.end_time
  }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除优惠券 "${row.name}" 吗？`, '提示')
    await api.admin.deleteCoupon(row.coupon_id)
    ElMessage.success('删除成功')
    loadCoupons()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

const submitForm = async () => {
  const payload = { ...form.value }
  // 确保时间字段为 ISO 字符串
  if (payload.start_time) payload.start_time = dayjs(payload.start_time).format('YYYY-MM-DDTHH:mm:ss')
  if (payload.end_time) payload.end_time = dayjs(payload.end_time).format('YYYY-MM-DDTHH:mm:ss')

  try {
    if (isEdit.value) {
      await api.admin.updateCoupon(currentId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await api.admin.createCoupon(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadCoupons()
  } catch (error) {
    console.error('提交失败:', error)
  }
}

onMounted(loadCoupons)
</script>

<style scoped>
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
