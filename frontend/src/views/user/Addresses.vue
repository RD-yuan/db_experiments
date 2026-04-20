<template>
  <div class="addresses-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>地址管理</span>
          <el-button type="primary" size="small" @click="handleAdd">
            新增地址
          </el-button>
        </div>
      </template>

      <el-table :data="addresses" style="width: 100%" v-loading="loading">
        <el-table-column prop="recipient_name" label="收件人" width="120" />
        <el-table-column prop="recipient_phone" label="电话" width="150" />
        <el-table-column prop="full_address" label="地址" />
        <el-table-column label="默认" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.address_id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="addresses.length === 0 && !loading" class="empty-tip">
        <el-empty description="暂无收货地址，请点击右上角新增" />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑地址' : '新增地址'"
      width="500px"
      @close="resetForm"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="收货人">
          <el-input v-model="form.recipient_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.recipient_phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="所在地区">
          <div style="display: flex; gap: 8px">
            <el-input v-model="form.province" placeholder="省" style="width: 30%" />
            <el-input v-model="form.city" placeholder="市" style="width: 30%" />
            <el-input v-model="form.district" placeholder="区/县" style="width: 30%" />
          </div>
        </el-form-item>
        <el-form-item label="详细地址">
          <el-input v-model="form.detail_address" type="textarea" placeholder="街道、门牌号等" />
        </el-form-item>
        <el-form-item label="邮政编码">
          <el-input v-model="form.postal_code" placeholder="选填" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'

// 地址列表数据
const addresses = ref([])
const loading = ref(false)

// 对话框相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const currentId = ref(null)

// 表单数据（字段名需与后端 Address 模型一致）
const defaultForm = () => ({
  recipient_name: '',
  recipient_phone: '',
  province: '',
  city: '',
  district: '',
  detail_address: '',
  postal_code: '',
  is_default: 0
})
const form = ref(defaultForm())

// 加载地址列表
const loadAddresses = async () => {
  loading.value = true
  try {
    const data = await api.user.getAddresses()
    addresses.value = data || []
  } catch (error) {
    console.error('加载地址失败', error)
    ElMessage.error('加载地址失败')
  } finally {
    loading.value = false
  }
}

// 新增地址
const handleAdd = () => {
  isEdit.value = false
  currentId.value = null
  form.value = defaultForm()
  dialogVisible.value = true
}

// 编辑地址
const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.address_id
  form.value = {
    recipient_name: row.recipient_name || '',
    recipient_phone: row.recipient_phone || '',
    province: row.province || '',
    city: row.city || '',
    district: row.district || '',
    detail_address: row.detail_address || '',
    postal_code: row.postal_code || '',
    is_default: row.is_default || 0
  }
  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  form.value = defaultForm()
  currentId.value = null
}

// 提交表单
const submitForm = async () => {
  // 基础校验
  if (!form.value.recipient_name || !form.value.recipient_phone ||
      !form.value.province || !form.value.city || !form.value.detail_address) {
    ElMessage.warning('请填写完整的收货信息')
    return
  }
  if (!/^1[3-9]\d{9}$/.test(form.value.recipient_phone)) {
    ElMessage.warning('请输入有效的手机号码')
    return
  }

  submitting.value = true
  try {
    if (isEdit.value) {
      await api.user.updateAddress(currentId.value, form.value)
      ElMessage.success('地址更新成功')
    } else {
      await api.user.addAddress(form.value)
      ElMessage.success('地址添加成功')
    }
    dialogVisible.value = false
    loadAddresses()
  } catch (error) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 删除地址
const handleDelete = async (addressId) => {
  try {
    await ElMessageBox.confirm('确定要删除该地址吗？', '提示', {
      type: 'warning'
    })
    await api.user.deleteAddress(addressId)
    ElMessage.success('删除成功')
    loadAddresses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

onMounted(() => {
  loadAddresses()
})
</script>

<style scoped>
.addresses-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.empty-tip {
  padding: 40px 0;
}
</style>