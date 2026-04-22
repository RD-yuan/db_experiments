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

          <el-form ref="profileFormRef" :model="profileForm" :rules="profileRules" label-width="90px">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
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
              <div class="asset-actions">
                <el-button type="warning" @click="openVipDialog">开通VIP</el-button>
                <el-button type="success" @click="rechargeDialogVisible = true">余额充值</el-button>
              </div>
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
            <div class="asset-item" v-if="vipActive">
              <span class="asset-label">当前权益</span>
              <span class="asset-value subtle">
                {{ discountText }} · {{ pointsRate }}倍积分
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

    <!-- 余额充值对话框 -->
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

    <!-- VIP套餐对话框 -->
    <el-dialog v-model="vipDialogVisible" title="选择VIP套餐" width="500px">
      <el-radio-group v-model="selectedPackage" class="vip-package-list">
        <el-radio
          v-for="(pkg, index) in vipPackages"
          :key="index"
          :label="index"
          border
          class="vip-package-item"
        >
          <div class="package-info">
            <span class="package-name">{{ pkg.name }} {{ pkg.months }}个月</span>
            <span class="package-price">¥{{ pkg.price.toFixed(2) }}</span>
          </div>
        </el-radio>
      </el-radio-group>
      <div class="balance-tip">当前余额：¥{{ formatMoney(profile.balance) }}</div>
      <template #footer>
        <el-button @click="vipDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="purchasing" @click="purchaseVip">确认购买</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const saving = ref(false)
const recharging = ref(false)
const rechargeDialogVisible = ref(false)
const profile = ref({})
const profileFormRef = ref(null)

const profileForm = reactive({
  username: '',
  email: '',
  phone: '',
  gender: 0,
  birthday: ''
})

const profileRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度需在 2 到 50 个字符之间', trigger: 'blur' }
  ],
  email: [
    {
      pattern: /^$|^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$/,
      message: '请输入正确的邮箱地址',
      trigger: 'blur'
    }
  ],
  phone: [
    { pattern: /^$|^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const rechargeForm = reactive({
  amount: 100
})

// VIP相关
const vipDialogVisible = ref(false)
const purchasing = ref(false)
const vipPackages = ref([])
const selectedPackage = ref(null)

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

const discountText = computed(() => {
  const level = profile.value?.vip_level || 0
  const discounts = { 1: '会员价', 2: '会员价享95折', 3: '会员价享9折' }
  return discounts[level] || '无折扣'
})

const pointsRate = computed(() => {
  const level = profile.value?.vip_level || 0
  const rates = { 1: 1.2, 2: 1.5, 3: 2.0 }
  return rates[level] || 1.0
})

const formatMoney = (value) => Number(value || 0).toFixed(2)

const syncForm = (data) => {
  profile.value = data || {}
  profileForm.username = profile.value.username || ''
  profileForm.email = profile.value.email || ''
  profileForm.phone = profile.value.phone || ''
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
  if (profileFormRef.value) {
    try {
      await profileFormRef.value.validate()
    } catch {
      return
    }
  }

  saving.value = true
  try {
    const res = await api.user.updateProfile({
      username: profileForm.username,
      email: profileForm.email || null,
      phone: profileForm.phone || null,
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

const openVipDialog = async () => {
  try {
    const res = await api.user.getVipPackages()
    vipPackages.value = res || []
    selectedPackage.value = null
    vipDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取套餐失败')
  }
}

const purchaseVip = async () => {
  if (selectedPackage.value === null) {
    ElMessage.warning('请选择一个套餐')
    return
  }
  const pkg = vipPackages.value[selectedPackage.value]
  try {
    await ElMessageBox.confirm(
      `确定使用余额购买 ${pkg.name} ${pkg.months}个月，支付 ¥${pkg.price.toFixed(2)}？`,
      '确认购买'
    )
  } catch {
    return
  }

  purchasing.value = true
  try {
    const res = await api.user.purchaseVip({ package_index: selectedPackage.value })
    syncForm(res)
    vipDialogVisible.value = false
    ElMessage.success('VIP开通成功！')
  } catch (error) {
    // 错误已由拦截器处理
  } finally {
    purchasing.value = false
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

.asset-actions {
  display: flex;
  gap: 10px;
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

.vip-package-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.vip-package-item {
  padding: 12px 16px !important;
  height: auto !important;
}

.package-info {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.package-name {
  font-weight: 500;
}

.package-price {
  color: #ff6700;
  font-size: 18px;
  font-weight: bold;
}

.balance-tip {
  margin-top: 16px;
  color: #606266;
}
</style>
