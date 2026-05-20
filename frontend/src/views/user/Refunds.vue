<template>
  <div class="my-refunds">
    <el-card><template #header><span>退货记录</span></template>
      <el-table :data="list" v-loading="loading">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column label="订单号" width="160"><template #default="{row}"><router-link :to="'/order/' + row.order_id">{{ row.order_id }}</router-link></template></el-table-column>
        <el-table-column prop="reason" label="退货原因" min-width="200" />
        <el-table-column label="状态" width="100"><template #default="{row}"><el-tag :type="['warning','success','danger'][row.status]" size="small">{{ ['待审核','已同意','已拒绝'][row.status] }}</el-tag></template></el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" />
        <el-table-column prop="create_time" label="申请时间" width="170"><template #default="{row}">{{ row.create_time?.slice(0,16) }}</template></el-table-column>
      </el-table>
      <el-empty v-if="list.length===0 && !loading" description="暂无退货记录" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/api'
const loading = ref(false)
const list = ref([])
onMounted(async () => {
  loading.value = true
  try {
    const r = await api.order.getMyRefunds()
    list.value = (r.items || []).filter(item => item.status !== undefined)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>
