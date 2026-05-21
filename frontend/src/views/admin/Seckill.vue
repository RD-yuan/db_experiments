<template>
  <div class="admin-seckill">
    <el-card style="margin-bottom:20px"><template #header><div style="display:flex;justify-content:space-between;align-items:center"><span>秒杀场次</span><el-button type="primary" size="small" @click="openSessionDialog()">新增场次</el-button></div></template>
      <el-table :data="sessions" v-loading="sLoading">
        <el-table-column prop="session_id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column label="开始时间" width="170"><template #default="{row}">{{ row.start_time?.slice(0,16) }}</template></el-table-column>
        <el-table-column label="结束时间" width="170"><template #default="{row}">{{ row.end_time?.slice(0,16) }}</template></el-table-column>
        <el-table-column label="状态" width="80"><template #default="{row}"><el-tag :type="row.status?'success':'danger'" size="small">{{ row.status?'启用':'禁用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="150"><template #default="{row}"><el-button size="small" @click="openSessionDialog(row)">编辑</el-button></template></el-table-column>
      </el-table>
    </el-card>

    <el-card><template #header><div style="display:flex;justify-content:space-between;align-items:center"><span>秒杀商品</span><el-button type="primary" size="small" @click="openSpDialog()">添加商品</el-button></div></template>
      <el-table :data="spList" v-loading="spLoading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="商品" min-width="160"><template #default="{row}">{{ row.product?.name }}</template></el-table-column>
        <el-table-column prop="seckill_price" label="秒杀价" width="100" />
        <el-table-column prop="seckill_stock" label="库存" width="80" />
        <el-table-column label="SKU" width="120"><template #default="{row}">{{ row.sku_spec_text || '不限' }}</template></el-table-column>
        <el-table-column prop="limit_per_user" label="限购" width="80" />
        <el-table-column label="操作" width="100"><template #default="{row}"><el-button size="small" type="danger" @click="deleteSp(row)">删除</el-button></template></el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="sessionDialog" :title="editingSession ? '编辑场次' : '新增场次'" width="500px">
      <el-form :model="sessionForm" label-width="100px">
        <el-form-item label="名称"><el-input v-model="sessionForm.name" /></el-form-item>
        <el-form-item label="开始时间"><el-date-picker v-model="sessionForm.start_time" type="datetime" placeholder="选择开始时间" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DDTHH:mm:ss" /></el-form-item>
        <el-form-item label="结束时间"><el-date-picker v-model="sessionForm.end_time" type="datetime" placeholder="选择结束时间" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DDTHH:mm:ss" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="sessionForm.status" :active-value="1" :inactive-value="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="sessionDialog=false">取消</el-button><el-button type="primary" @click="saveSession">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="spDialog" title="添加秒杀商品" width="500px">
      <el-form :model="spForm" label-width="100px">
        <el-form-item label="场次"><el-select v-model="spForm.session_id" placeholder="选择场次"><el-option v-for="s in sessions" :key="s.session_id" :label="s.name" :value="s.session_id" /></el-select></el-form-item>
        <el-form-item label="商品ID">
          <div style="display:flex;gap:8px">
            <el-input-number v-model="spForm.product_id" :min="1" @change="onProductIdChange" style="flex:1" />
            <el-button @click="loadProductSkus" :loading="skuLoading">加载规格</el-button>
          </div>
        </el-form-item>
        <el-form-item label="SKU" v-if="skuList.length > 0"><div style="display:flex;gap:8px;width:100%">
          <el-select v-model="spForm.sku_id" placeholder="选择规格（可选）" clearable @change="onSkuSelected"><el-option v-for="s in skuList" :key="s.sku_id" :label="s.spec_text + ` (库存${s.stock})`" :value="s.sku_id" /></el-select><span v-if="selectedSkuStock > 0" style="color:#999;line-height:32px;white-space:nowrap">库存: {{ selectedSkuStock }}</span></div>
        </el-form-item>
        <el-form-item label="秒杀价"><el-input-number v-model="spForm.seckill_price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="spForm.seckill_stock" :min="0" /><span v-if="selectedSkuStock > 0" style="margin-left:8px;color:#909399;font-size:12px">可用库存: {{ selectedSkuStock }}</span></el-form-item>
        <el-form-item label="限购"><el-input-number v-model="spForm.limit_per_user" :min="1" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="spDialog=false">取消</el-button><el-button type="primary" @click="saveSp">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
const sessions = ref([])
const sLoading = ref(false)
const sessionDialog = ref(false)
const editingSession = ref(null)
const sessionForm = ref({ name: '', start_time: '', end_time: '', status: 1 })
const spList = ref([])
const spLoading = ref(false)
const spDialog = ref(false)
const spForm = ref({ session_id: '', product_id: 0, sku_id: null, seckill_price: 0, seckill_stock: 0, limit_per_user: 1 })
const skuList = ref([])
const skuLoading = ref(false)
const selectedSkuStock = ref(0)
const onSkuSelected = (val) => { if (val) { const s = skuList.value.find(x => x.sku_id === val); if (s) selectedSkuStock.value = (s.available_stock !== undefined ? s.available_stock : s.stock) || 0 } else { selectedSkuStock.value = 0 } }
const onProductIdChange = () => { skuList.value = []; spForm.value.sku_id = null; selectedSkuStock.value = 0 }
const loadProductSkus = async () => { const pid = spForm.value.product_id; if (!pid) { skuList.value = []; return; } skuLoading.value = true; try { const data = await api.product.getDetail(pid); if (data && data.skus && data.skus.length > 0) { skuList.value = data.skus } else { skuList.value = []; if (data && data.stock > 0) { selectedSkuStock.value = data.available_stock !== undefined ? data.available_stock : data.stock } } } catch(e) { skuList.value = []; ElMessage.error('加载失败') } finally { skuLoading.value = false } }

const loadSessions = async () => {
  sLoading.value = true
  try {
    sessions.value = await api.admin.getSeckillSessions()
  } catch (e) {
    console.error(e)
  } finally {
    sLoading.value = false
  }
}

const loadSp = async () => {
  spLoading.value = true
  try {
    const r = await api.admin.getSeckillProducts({})
    spList.value = r.items
  } catch (e) {
    console.error(e)
  } finally {
    spLoading.value = false
  }
}

const openSessionDialog = (row) => {
  editingSession.value = row || null
  sessionForm.value = row ? { ...row } : { name: '', start_time: '', end_time: '', status: 1 }
  sessionDialog.value = true
}

const saveSession = async () => {
  try {
    if (editingSession.value) {
      await api.admin.updateSeckillSession(editingSession.value.session_id, sessionForm.value)
    } else {
      await api.admin.createSeckillSession(sessionForm.value)
    }
    ElMessage.success('保存成功')
    sessionDialog.value = false
    loadSessions()
  } catch (e) {
    console.error(e)
  }
}

const openSpDialog = () => {
  spForm.value = { session_id: sessions.value[0]?.session_id || '', product_id: 0, sku_id: null, seckill_price: 0, seckill_stock: 0, limit_per_user: 1 }; skuList.value = []; selectedSkuStock.value = 0
  spDialog.value = true
}

const saveSp = async () => {
  try {
    await api.admin.addSeckillProduct(spForm.value)
    ElMessage.success('添加成功')
    spDialog.value = false
    loadSp()
  } catch (e) {
    console.error(e)
  }
}

const deleteSp = async (row) => {
  try {
    await api.admin.deleteSeckillProduct(row.id)
    ElMessage.success('已删除')
    loadSp()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => { loadSessions(); loadSp() })
</script>
