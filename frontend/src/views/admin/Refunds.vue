<template>
  <div class="admin-refunds">
    <el-card>
      <template #header><span>退货管理</span></template>
      <el-radio-group v-model="statusFilter" size="small" @change="load">
        <el-radio-button :value="null">全部</el-radio-button>
        <el-radio-button :value="0">待审核</el-radio-button>
        <el-radio-button :value="1">已同意</el-radio-button>
        <el-radio-button :value="2">已拒绝</el-radio-button>
      </el-radio-group>
      <el-table :data="list" v-loading="loading" style="margin-top:15px">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="order_id" label="订单号" width="160" />
        <el-table-column label="用户" width="120"><template #default="{row}">{{ row.username }}</template></el-table-column>
        <el-table-column prop="reason" label="退货原因" min-width="200" />
        <el-table-column label="状态" width="100"><template #default="{row}"><el-tag :type="['warning','success','danger'][row.status]" size="small">{{ ['待审核','已同意','已拒绝'][row.status] }}</el-tag></template></el-table-column>
        <el-table-column prop="create_time" label="申请时间" width="170"><template #default="{row}">{{ row.create_time?.slice(0,16) }}</template></el-table-column>
        <el-table-column label="操作" width="220" fixed="right"><template #default="{row}">
          <template v-if="row.status===0">
            <el-button size="small" type="success" @click="approve(row)">同意</el-button>
            <el-button size="small" type="danger" @click="reject(row)">拒绝</el-button>
          </template>
          <span v-else-if="row.status===1" style="color:#67c23a">{{ row.remark || '已同意' }}</span>
          <span v-else style="color:#f56c6c">{{ row.remark || '已拒绝' }}</span>
        </template></el-table-column>
      </el-table>
      <el-pagination v-if="total>0" v-model:current-page="page" :page-size="20" :total="total" layout="total,prev,pager,next" @current-change="load" style="margin-top:20px;justify-content:flex-end" />
    </el-card>
  </div>
</template>

<script setup>

import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
const loading = ref(false)
const list = ref([])
const page = ref(1)
const total = ref(0)
const statusFilter = ref(null)

const load = async () => {
  loading.value = true
  try {
    const r = await api.admin.getRefunds({ page: page.value, status: statusFilter.value })
    list.value = r.items
    total.value = r.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const approve = async (row) => {
  try {
    const { value: remark } = await ElMessageBox.prompt('备注（可选）', '同意退货', { confirmButtonText: '确定' })
    await api.admin.processRefund(row.id, { status: 1, remark: remark || '' })
    ElMessage.success('已同意退货退款')
    load()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const reject = async (row) => {
  try {
    const { value: remark } = await ElMessageBox.prompt('拒绝原因', '拒绝退货', { confirmButtonText: '确定' })
    await api.admin.processRefund(row.id, { status: 2, remark: remark || '' })
    ElMessage.success('已拒绝')
    load()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

onMounted(load)
</script>
