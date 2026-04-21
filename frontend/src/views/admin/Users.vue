<template>
  <div class="admin-users">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>用户管理</span>
          <el-input
            v-model="keyword"
            placeholder="搜索用户名/手机/邮箱"
            style="width: 300px"
            clearable
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch">搜索</el-button>
            </template>
          </el-input>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="user_id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="phone" label="手机号" width="140" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column label="会员卡" width="110">
          <template #default="{ row }">
            <el-tag v-if="row.vip_active" type="warning" size="small">
              {{ vipCardName(row.vip_level) }}
            </el-tag>
            <el-tag v-else-if="row.is_vip" type="info" size="small">已过期</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="会员到期" width="180">
          <template #default="{ row }">
            {{ formatVipExpiry(row.vip_expire_time) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="管理员" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_admin" type="primary" size="small">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleToggleStatus(row)">
              {{ row.status === 1 ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" type="warning" @click="handleSetVip(row)">设置VIP</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          :page-size="perPage"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadUsers"
        />
      </div>
    </el-card>

    <!-- 设置VIP对话框 -->
    <el-dialog v-model="vipDialogVisible" title="设置VIP" width="400px">
      <el-form :model="vipForm" label-width="100px">
        <el-form-item label="用户">
          <span>{{ currentUser?.username }}</span>
        </el-form-item>
        <el-form-item label="会员状态">
          <el-switch
            v-model="vipForm.is_vip"
            :active-value="1"
            :inactive-value="0"
            active-text="发放"
            inactive-text="取消"
          />
        </el-form-item>
        <el-form-item label="会员等级">
          <el-select v-model="vipForm.vip_level" placeholder="请选择" :disabled="!vipForm.is_vip">
            <el-option label="银卡" :value="1" />
            <el-option label="金卡" :value="2" />
            <el-option label="钻石卡" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="有效期(月)">
          <el-input-number v-model="vipForm.vip_months" :min="1" :max="120" :disabled="!vipForm.is_vip" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="vipDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitVip">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const page = ref(1)
const perPage = ref(20)
const total = ref(0)
const keyword = ref('')

const vipDialogVisible = ref(false)
const currentUser = ref(null)
const vipForm = ref({
  is_vip: 1,
  vip_level: 1,
  vip_months: 1
})

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm')

const vipCardName = (level) => {
  const names = {
    1: '银卡',
    2: '金卡',
    3: '钻石卡'
  }
  return names[level] || '会员'
}

const formatVipExpiry = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await api.admin.getUsers({
      page: page.value,
      per_page: perPage.value,
      keyword: keyword.value
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载用户失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  loadUsers()
}

const handleToggleStatus = async (row) => {
  const newStatus = row.status === 1 ? 0 : 1
  const action = newStatus === 1 ? '启用' : '禁用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 "${row.username}" 吗？`, '提示')
    await api.admin.updateUserStatus(row.user_id, { status: newStatus })
    ElMessage.success(`已${action}`)
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
    }
  }
}

const handleSetVip = (row) => {
  currentUser.value = row
  vipForm.value = {
    is_vip: row.is_vip ? 1 : 0,
    vip_level: row.vip_level || 1,
    vip_months: 1
  }
  vipDialogVisible.value = true
}

const submitVip = async () => {
  try {
    const payload = vipForm.value.is_vip
      ? vipForm.value
      : { is_vip: 0, vip_level: 0, vip_months: 0 }
    await api.admin.setUserVip(currentUser.value.user_id, payload)
    ElMessage.success(vipForm.value.is_vip ? '会员卡设置成功' : '会员资格已取消')
    vipDialogVisible.value = false
    loadUsers()
  } catch (error) {
    console.error('设置VIP失败:', error)
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
