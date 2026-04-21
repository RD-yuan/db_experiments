<template>
  <div class="admin-orders">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>订单管理</span>
          <el-select v-model="statusFilter" placeholder="订单状态" clearable style="width: 150px" @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="待支付" :value="0" />
            <el-option label="已支付" :value="1" />
            <el-option label="已发货" :value="2" />
            <el-option label="已完成" :value="3" />
            <el-option label="已取消" :value="4" />
          </el-select>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="order_id" label="订单号" width="200" />
        <el-table-column prop="payment_amount" label="实付金额" width="120">
          <template #default="{ row }">¥{{ row.payment_amount }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="下单时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleDetail(row)">查看</el-button>
            <el-button
              v-if="row.status === 1"
              size="small"
              type="primary"
              @click="handleShip(row)"
            >
              发货
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
          @current-change="loadOrders"
        />
      </div>
    </el-card>

    <!-- 发货对话框 -->
    <el-dialog v-model="shipDialogVisible" title="发货" width="400px">
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="订单号">
          <span>{{ currentOrder?.order_id }}</span>
        </el-form-item>
        <el-form-item label="物流公司">
          <el-input v-model="shipForm.shipping_company" placeholder="如：顺丰速运" />
        </el-form-item>
        <el-form-item label="物流单号">
          <el-input v-model="shipForm.shipping_number" placeholder="请输入快递单号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shipDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitShip">确认发货</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const page = ref(1)
const perPage = ref(20)
const total = ref(0)
const statusFilter = ref('')

const shipDialogVisible = ref(false)
const currentOrder = ref(null)
const shipForm = ref({
  shipping_company: '',
  shipping_number: ''
})

const getStatusType = (status) => {
  const types = { 0: 'warning', 1: 'primary', 2: 'info', 3: 'success', 4: 'info', 5: 'danger' }
  return types[status] || 'info'
}

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm')

const loadOrders = async () => {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (statusFilter.value !== '') {
      params.status = statusFilter.value
    }
    const res = await api.admin.getOrders(params)
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载订单失败:', error)
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  page.value = 1
  loadOrders()
}

const handleDetail = (row) => {
  router.push(`/order/${row.order_id}`)
}

const handleShip = (row) => {
  currentOrder.value = row
  shipForm.value = { shipping_company: '', shipping_number: '' }
  shipDialogVisible.value = true
}

const submitShip = async () => {
  if (!shipForm.value.shipping_company || !shipForm.value.shipping_number) {
    ElMessage.warning('请填写完整物流信息')
    return
  }
  try {
    await api.admin.shipOrder(currentOrder.value.order_id, shipForm.value)
    ElMessage.success('发货成功')
    shipDialogVisible.value = false
    loadOrders()
  } catch (error) {
    console.error('发货失败:', error)
  }
}

onMounted(loadOrders)
</script>

<style scoped>
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>