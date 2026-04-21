<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <el-col :xs="24" :md="14">
        <el-card class="info-card" v-loading="loading">
          <template #header>
            <div class="card-header">
              <span>个人信息</span>
              <el-button type="primary" :loading="saving" @click="saveProfile">保存修改</el-button>
            </div>
          </template>

          <el-form :model="profileForm" label-width="90px">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input :model-value="profile.email || '-'" disabled />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input :model-value="profile.phone || '-'" disabled />
            </el-form-item>
            <el-form-item label="性别">
              <el-select v-model="profileForm.gender" placeholder="请选择性别">
                <el-option label="未知" :value="0" />
                <el-option label="男" :value="1" />
                <el-option label="女" :value="2" />
              </el-select>
            </el-form-item>
            <el-form-item label="生日">
              <el-date-picker
                v-model="profileForm.birthday"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="请选择生日"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="10">
        <el-card class="wallet-card" v-loading="loading">
          <template #header>
            <div class="card-header">
              <span>账户资产</span>
              <el-button type="success" @click="rechargeDialogVisible = true">余额充值</el-button>
            </div>
          </template>

          <div class="asset-list">
            <div class="asset-item">
              <span class="asset-label">余额</span>
              <span class="asset-value">¥{{ formatMoney(profile.balance) }}</span>
            </div>
            <div class="asset-item">
              <span class="asset-label">积分</span>
              <span class="asset-value">{{ profile.points || 0 }}</span>
            </div>
            <div class="asset-item">
              <span class="asset-label">会员资格</span>
              <span>
                <el-tag :type="vipActive ? 'warning' : 'info'">
                  {{ vipActive ? profile.vip_level_text : '非会员' }}
                </el-tag>
              </span>
            </div>
            <div class="asset-item">
              <span class="asset-label">到期时间</span>
              <span class="asset-value subtle">{{ vipExpireText }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="rechargeDialogVisible" title="余额充值" width="420px">
      <el-form :model="rechargeForm" label-width="80px">
        <el-form-item label="充值金额">
          <el-input-number
            v-model="rechargeForm.amount"
            :min="0.01"
            :precision="2"
            :step="10"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rechargeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="recharging" @click="submitRecharge">确认充值</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const saving = ref(false)
const recharging = ref(false)
const rechargeDialogVisible = ref(false)
const profile = ref({})

const profileForm = reactive({
  username: '',
  gender: 0,
  birthday: ''
})

const rechargeForm = reactive({
  amount: 100
})

const vipActive = computed(() => {
  if (!profile.value?.vip_active) return false
  if (!profile.value.vip_expire_time) return true
  return new Date(profile.value.vip_expire_time).getTime() > Date.now()
})

const vipExpireText = computed(() => {
  if (!vipActive.value) return '暂无有效会员'
  if (!profile.value.vip_expire_time) return '长期有效'
  return new Date(profile.value.vip_expire_time).toLocaleString()
})

const formatMoney = (value) => Number(value || 0).toFixed(2)

const syncForm = (data) => {
  profile.value = data || {}
  profileForm.username = profile.value.username || ''
  profileForm.gender = profile.value.gender ?? 0
  profileForm.birthday = profile.value.birthday || ''
  userStore.setUser(profile.value)
}

const loadProfile = async () => {
  loading.value = true
  try {
    const res = await api.user.getProfile()
    syncForm(res)
  } finally {
    loading.value = false
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    const res = await api.user.updateProfile({
      username: profileForm.username,
      gender: profileForm.gender,
      birthday: profileForm.birthday || null
    })
    syncForm(res)
    ElMessage.success('个人信息已更新')
  } finally {
    saving.value = false
  }
}

const submitRecharge = async () => {
  if (!rechargeForm.amount || rechargeForm.amount <= 0) {
    ElMessage.warning('请输入有效充值金额')
    return
  }

  recharging.value = true
  try {
    const res = await api.user.recharge({ amount: rechargeForm.amount })
    profile.value.balance = res.new_balance
    userStore.setUser({ ...(userStore.user || {}), balance: res.new_balance })
    rechargeDialogVisible.value = false
    ElMessage.success('充值成功')
  } finally {
    recharging.value = false
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-page {
  padding: 20px;
}

.info-card,
.wallet-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.asset-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.asset-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.asset-label {
  color: #606266;
}

.asset-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.asset-value.subtle {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
}
</style>
