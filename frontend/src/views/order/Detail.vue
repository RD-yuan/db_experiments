<template>
  <div class="order-detail" v-loading="loading">
    <el-card v-if="order">
      <template #header>
        <span>订单详情 #{{ order.order_id }}</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ order.order_id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType">{{ order.status_text }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(order.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="实付金额">¥{{ order.payment_amount }}</el-descriptions-item>
        <el-descriptions-item v-if="order.status === 0" label="当前余额">
          ¥{{ formatMoney(userStore.user?.balance) }}
        </el-descriptions-item>
        <el-descriptions-item label="运费">¥{{ order.freight_amount }}</el-descriptions-item>
        <el-descriptions-item label="优惠金额">¥{{ order.discount_amount }}</el-descriptions-item>
        <el-descriptions-item v-if="order.points_used" label="使用积分">{{ order.points_used }}</el-descriptions-item>
        <el-descriptions-item v-if="order.address_snapshot" label="收货信息">
          {{ addressDisplay }}
        </el-descriptions-item>
      </el-descriptions>

      <h3 style="margin-top: 20px">商品列表</h3>
      <el-table :data="order.items" style="width: 100%">
        <el-table-column label="商品名称">
          <template #default="{ row }">
            {{ row.product_name }}
            <span v-if="row.sku_spec_text" style="color: #999; font-size: 12px">{{ row.sku_spec_text }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="单价" width="120">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column label="小计" width="120">
          <template #default="{ row }">¥{{ row.subtotal }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" v-if="order.status === 3 && order.user_id === userStore.user?.user_id">
          <template #default="{ row }">
            <el-button v-if="!row.is_reviewed" type="primary" text @click="openReviewDialog(row)">评价</el-button>
            <template v-else>
              <el-button type="primary" text @click="openReviewDialog(row, true)">修改</el-button>
              <el-button
                v-if="!getReviewForItem(row.order_item_id)?.follow_up_comment"
                type="success" text @click="openFollowUpDialog(row)"
              >追评</el-button>
              <el-button type="danger" text @click="handleDeleteReview(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 20px; text-align: right">
        <el-button v-if="order.status === 0" type="primary" @click="handlePay">立即支付</el-button>
        <el-button v-if="order.status === 0" @click="handleCancel">取消订单</el-button>
        <el-button v-if="order.status === 2 && order.user_id === userStore.user?.user_id" type="primary" @click="handleReceive">确认收货</el-button>
        <el-button v-if="canRefund" type="warning" @click="handleRefund">申请退货</el-button>
        <el-button @click="$router.back()">返回</el-button>
      </div>
    </el-card>

    <el-dialog v-model="reviewDialogVisible" :title="currentReviewId ? '修改评价' : '发表评价'" width="500px">
      <el-form :model="reviewForm" label-width="80px">
        <el-form-item label="评分">
          <el-rate v-model="reviewForm.rating" show-text />
        </el-form-item>
        <el-form-item label="评价内容">
          <el-input v-model="reviewForm.comment" type="textarea" :rows="4" placeholder="请输入您的使用感受..." />
        </el-form-item>
        <el-form-item label="上传图片">
          <div style="display:flex;flex-wrap:wrap;gap:8px">
            <div v-for="(url, idx) in reviewForm.images" :key="idx" style="position:relative;width:80px;height:80px">
              <el-image :src="url" fit="cover" style="width:80px;height:80px;border-radius:4px" />
              <el-button size="small" circle type="danger" style="position:absolute;top:-6px;right:-6px" @click="reviewForm.images.splice(idx,1)">×</el-button>
            </div>
            <el-upload
              v-if="reviewForm.images.length < 6"
              :show-file-list="false"
              :http-request="(opt) => uploadReviewImg(opt, 'review')"
              accept="image/*"
            >
              <div style="width:80px;height:80px;border:1px dashed #d9d9d9;border-radius:4px;display:flex;align-items:center;justify-content:center;cursor:pointer">
                <span style="font-size:24px;color:#999">+</span>
              </div>
            </el-upload>
          </div>
        </el-form-item>
        <el-form-item label="匿名评价">
          <el-switch v-model="reviewForm.is_anonymous" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview" :loading="submitting">提交</el-button>
      </template>
    </el-dialog>

    <!-- 追评对话框 -->
    <el-dialog v-model="followUpVisible" title="追加评价" width="500px">
      <el-form :model="followUpForm" label-width="80px">
        <el-form-item label="追评内容">
          <el-input v-model="followUpForm.comment" type="textarea" :rows="4" placeholder="使用一段时间后的感受..." />
        </el-form-item>
        <el-form-item label="上传图片">
          <div style="display:flex;flex-wrap:wrap;gap:8px">
            <div v-for="(url, idx) in followUpForm.images" :key="idx" style="position:relative;width:80px;height:80px">
              <el-image :src="url" fit="cover" style="width:80px;height:80px;border-radius:4px" />
              <el-button size="small" circle type="danger" style="position:absolute;top:-6px;right:-6px" @click="followUpForm.images.splice(idx,1)">×</el-button>
            </div>
            <el-upload
              v-if="followUpForm.images.length < 6"
              :show-file-list="false"
              :http-request="(opt) => uploadReviewImg(opt, 'followUp')"
              accept="image/*"
            >
              <div style="width:80px;height:80px;border:1px dashed #d9d9d9;border-radius:4px;display:flex;align-items:center;justify-content:center;cursor:pointer">
                <span style="font-size:24px;color:#999">+</span>
              </div>
            </el-upload>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="followUpVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFollowUp" :loading="submitting">提交追评</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const order = ref(null)
const reviewDialogVisible = ref(false)
const submitting = ref(false)
const currentOrderItem = ref(null)
const currentReviewId = ref(null)

// 追评
const followUpVisible = ref(false)
const followUpForm = ref({ comment: '', images: [] })
const followUpReviewId = ref(null)
const myReviews = ref([])

const getReviewForItem = (orderItemId) => {
  return myReviews.value.find(r => r.order_item_id === orderItemId) || null
}

const reviewForm = ref({ rating: 5, comment: '', images: [], is_anonymous: false })

const canRefund = computed(() => { if (!order.value || order.value.user_id !== userStore.user?.user_id) return false; if (order.value.status !== 1 && order.value.status !== 3) return false; return true })

const statusType = computed(() => {
  const types = { 0: 'warning', 1: 'primary', 2: 'info', 3: 'success', 4: 'info', 5: 'danger', 6: 'warning' }
  return types[order.value?.status] || 'info'
})

const addressDisplay = computed(() => {
  if (!order.value?.address_snapshot) return ''
  try {
    const addr = JSON.parse(order.value.address_snapshot)
    return `${addr.recipient_name} ${addr.recipient_phone} ${addr.full_address || addr.detail_address}`
  } catch { return order.value.address_snapshot }
})

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')
const formatMoney = (value) => Number(value || 0).toFixed(2)

const parseReviewImages = (imgs) => {
  if (!imgs) return []
  try { return JSON.parse(imgs) } catch { return imgs.split(',').filter(Boolean) }
}

const uploadReviewImg = async (opt, target) => {
  try {
    const res = await api.review.uploadImage(opt.file)
    if (target === 'followUp') followUpForm.value.images.push(res.url)
    else reviewForm.value.images.push(res.url)
  } catch (e) { console.error('上传失败', e) }
}

const loadOrder = async () => {
  loading.value = true
  try {
    order.value = await api.order.getDetail(String(route.params.id))
    if (order.value?.status === 3) loadMyReviews()
  } catch (error) {
    ElMessage.error('订单不存在')
    router.replace('/orders')
  } finally { loading.value = false }
}

const handlePay = async () => {
  try {
    await ElMessageBox.confirm(
      `将使用账户余额支付 ¥${formatMoney(order.value.payment_amount)}，当前余额 ¥${formatMoney(userStore.user?.balance)}。确定支付吗？`,
      '余额支付',
      { type: 'warning' }
    )
    await api.order.pay(String(order.value.order_id))
    ElMessage.success('支付成功')
    await userStore.ensureSession(true)
    loadOrder()
  } catch (error) {
    if (error !== 'cancel') console.error('支付失败:', error)
  }
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm('确定要取消订单吗?', '提示')
    await api.order.cancel(String(order.value.order_id))
    ElMessage.success('订单已取消')
    loadOrder()
  } catch (error) { if (error !== 'cancel') console.error('取消订单失败:', error) }
}

const handleReceive = async () => {
  try {
    await ElMessageBox.confirm('确认已收到商品吗?', '提示')
    await api.order.receive(String(order.value.order_id))
    ElMessage.success('确认收货成功')
    loadOrder()
  } catch (error) { if (error !== 'cancel') console.error('确认收货失败:', error) }
}

const openReviewDialog = async (item, isEdit = false) => {
  currentOrderItem.value = item
  if (isEdit) {
    if (!myReviews.value.length) await loadMyReviews()
    const existing = getReviewForItem(item.order_item_id)
    if (existing) {
      currentReviewId.value = existing.review_id
      reviewForm.value = {
        rating: existing.rating,
        comment: existing.comment || '',
        images: parseReviewImages(existing.images),
        is_anonymous: !!existing.is_anonymous
      }
    } else {
      ElMessage.error('未找到评价记录')
      return
    }
  } else {
    currentReviewId.value = null
    reviewForm.value = { rating: 5, comment: '', images: [], is_anonymous: false }
  }
  reviewDialogVisible.value = true
}

const submitReview = async () => {
  if (!reviewForm.value.rating) return ElMessage.warning('请选择评分')
  if (!reviewForm.value.comment.trim()) return ElMessage.warning('请输入评价内容')
  submitting.value = true
  try {
    if (currentReviewId.value) {
      await api.review.update(currentReviewId.value, {
        rating: reviewForm.value.rating,
        comment: reviewForm.value.comment.trim(),
        images: reviewForm.value.images,
        is_anonymous: reviewForm.value.is_anonymous
      })
      ElMessage.success('评价已更新')
    } else {
      await api.review.create({
        order_item_id: currentOrderItem.value.order_item_id,
        rating: reviewForm.value.rating,
        comment: reviewForm.value.comment.trim(),
        images: reviewForm.value.images,
        is_anonymous: reviewForm.value.is_anonymous
      })
      ElMessage.success('评价成功')
    }
    reviewDialogVisible.value = false
    loadOrder()
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleDeleteReview = async (item) => {
  try {
    await ElMessageBox.confirm('确定要删除该评价吗？', '提示')
    const target = getReviewForItem(item.order_item_id)
    if (!target) { ElMessage.error('未找到评价记录'); return }
    await api.review.delete(target.review_id)
    ElMessage.success('评价已删除')
    myReviews.value = myReviews.value.filter(r => r.review_id !== target.review_id)
    loadOrder()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败', error)
  }
}

const loadMyReviews = async () => {
  try {
    const res = await api.review.getMy({ page: 1, per_page: 200 })
    myReviews.value = res.items || []
  } catch { myReviews.value = [] }
}

const openFollowUpDialog = async (item) => {
  await loadMyReviews()
  const review = getReviewForItem(item.order_item_id)
  if (!review) { ElMessage.error('未找到评价记录'); return }
  if (review.follow_up_comment) { ElMessage.warning('已追评过'); return }
  followUpReviewId.value = review.review_id
  followUpForm.value = { comment: '', images: [] }
  followUpVisible.value = true
}

const submitFollowUp = async () => {
  if (!followUpForm.value.comment.trim()) { ElMessage.warning('请输入追评内容'); return }
  submitting.value = true
  try {
    await api.review.addFollowUp(followUpReviewId.value, {
      comment: followUpForm.value.comment,
      images: followUpForm.value.images
    })
    ElMessage.success('追评成功')
    followUpVisible.value = false
    loadOrder()
    loadMyReviews()
  } catch (error) { console.error('追评失败:', error) }
  finally { submitting.value = false }
}

const handleRefund = async () => { try { const { value: reason } = await ElMessageBox.prompt('请填写退货原因', '申请退货', { confirmButtonText: '提交' }); await api.order.applyRefund(String(order.value.order_id), { reason }); ElMessage.success('退货申请已提交'); loadOrder() } catch(e) { if (e !== 'cancel') console.error(e) } }

onMounted(loadOrder)
</script>
