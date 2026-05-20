<template>
  <div class="seckill-page">
    <div v-if="!data.session" class="empty-tip"><el-empty description="暂无秒杀活动" /></div>
    <template v-else>
      <div class="seckill-header">
        <h2>{{ data.session.name }}</h2>
        <div class="countdown">距结束 <span class="time">{{ countdown }}</span></div>
      </div>
      <div class="product-grid">
        <div v-for="sp in data.products" :key="sp.id" class="seckill-item">
          <div class="sp-image"><el-image :src="sp.product?.main_image || ''" fit="cover"><template #error><div class="img-placeholder">No Image</div></template></el-image></div>
          <div class="sp-info">
            <h4>{{ sp.product?.name }}</h4>
            <div class="sp-price"><span class="seckill-price">秒杀价 ¥{{ sp.seckill_price }}</span><span class="orig-price">¥{{ sp.product?.price }}</span></div>
            <div class="sp-stock">剩余 {{ sp.seckill_stock }} 件</div>
            <el-button type="danger" size="small" :disabled="sp.seckill_stock<=0" @click="buy(sp)">立即抢购</el-button>
          </div>
        </div>
      </div>
    </template>

    <el-dialog v-model="orderDialog" title="确认下单" width="480px">
      <el-form label-width="80px">
        <el-form-item label="商品">{{ currentSp?.product?.name }}</el-form-item>
        <el-form-item label="价格">¥{{ currentSp?.seckill_price }}</el-form-item>

        <!-- SKU 选择 -->
        <template v-if="currentProduct?.has_sku && skuTemplates.length > 0">
          <el-form-item v-for="tpl in skuTemplates" :key="tpl.template_id" :label="tpl.name">
            <el-radio-group v-model="selectedSpecs[tpl.template_id]" @change="onSkuChange">
              <el-radio-button v-for="val in tpl.values" :key="val.value_id" :value="val.value_id">
                {{ val.value }}
              </el-radio-button>
            </el-radio-group>
          </el-form-item>
        </template>

        <el-form-item label="数量">
          <el-input-number v-model="qty" :min="1" :max="maxQty" />
        </el-form-item>
        <el-form-item label="地址">
          <el-select v-model="addrId" placeholder="选择收货地址">
            <el-option v-for="a in addresses" :key="a.address_id" :label="a.full_address" :value="a.address_id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="orderDialog=false">取消</el-button>
        <el-button type="danger" @click="submitOrder" :disabled="!addrId || !canSubmit">确认下单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api'

const router = useRouter()
const data = ref({ session: null, products: [] })
const countdown = ref('')
const orderDialog = ref(false)
const currentSp = ref(null)
const qty = ref(1)
const addrId = ref(null)
const addresses = ref([])
const selectedSpecs = ref({})
const currentSku = ref(null)
const skuTemplates = ref([])
let timer = null

const currentProduct = computed(() => currentSp.value?.product || null)

const maxQty = computed(() => {
  if (!currentSp.value) return 1
  const seckillLimit = currentSp.value.seckill_stock || 0
  if (currentProduct.value?.has_sku) {
    if (currentSku.value) {
      return Math.min(seckillLimit, currentSku.value.stock || 0)
    }
    return seckillLimit
  }
  return seckillLimit
})

const canSubmit = computed(() => {
  if (!currentProduct.value?.has_sku) return true
  // 有 SKU 则必须选完所有规格
  if (skuTemplates.value.length === 0) return true
  return Object.keys(selectedSpecs.value).length === skuTemplates.value.length
    && Object.values(selectedSpecs.value).every(Boolean)
})

const findMatchingSku = () => {
  if (!currentProduct.value?.skus) return null
  const selIds = Object.values(selectedSpecs.value).filter(Boolean)
  if (selIds.length === 0) return null
  return currentProduct.value.skus.find(sku => {
    let ids = sku.spec_ids
    if (typeof ids === 'string') ids = JSON.parse(ids)
    if (selIds.length !== ids.length) return false
    return selIds.every(id => ids.includes(id))
  }) || null
}

const onSkuChange = () => {
  currentSku.value = findMatchingSku()
  qty.value = 1
}

const load = async () => {
  try {
    data.value = await api.seckill.getCurrent()
    if (data.value.session) startCountdown()
  } catch (e) { console.error(e) }
}

const startCountdown = () => {
  const tick = () => {
    const diff = new Date(data.value.session.end_time).getTime() - Date.now()
    if (diff <= 0) { countdown.value = '已结束'; clearInterval(timer); return }
    const h = Math.floor(diff / 3600000), m = Math.floor((diff % 3600000) / 60000), s = Math.floor((diff % 60000) / 1000)
    countdown.value = h + ':' + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0')
  }
  tick(); timer = setInterval(tick, 1000)
}

const loadSkuTemplates = async () => {
  if (!currentProduct.value?.has_sku || !currentProduct.value?.skus?.length) {
    skuTemplates.value = []
    return
  }
  try {
    let templates = await api.product.getSpecTemplates()
    if (!templates || !templates.length) {
      // Fallback: build from SKU spec_text
      const groups = {}
      currentProduct.value.skus.forEach(sku => {
        const text = sku.spec_text || ''
        text.split(' / ').filter(Boolean).forEach((part, idx) => {
          const ci = part.indexOf(':')
          const gid = ci > 0 ? part.substring(0, ci) : '规格' + (idx + 1)
          const gval = ci > 0 ? part.substring(ci + 1) : part
          if (!groups[gid]) groups[gid] = new Set()
          groups[gid].add(gval)
        })
      })
      let fid = 90000
      templates = Object.entries(groups).map(([name, values]) => ({
        template_id: fid++,
        name,
        values: [...values].map(v => ({ value_id: fid++, value: v }))
      }))
    } else {
      const usedSpecIds = new Set()
      currentProduct.value.skus.forEach(sku => {
        let ids = sku.spec_ids
        if (typeof ids === 'string') ids = JSON.parse(ids)
        if (ids) ids.forEach(id => usedSpecIds.add(id))
      })
      templates = templates
        .map(tpl => ({ ...tpl, values: tpl.values.filter(v => usedSpecIds.has(v.value_id)) }))
        .filter(tpl => tpl.values.length > 0)
    }
    skuTemplates.value = templates
  } catch (e) { console.error(e) }
}

const buy = async (sp) => {
  currentSp.value = sp
  qty.value = 1
  addrId.value = null
  selectedSpecs.value = {}
  currentSku.value = null
  await loadSkuTemplates()
  try { addresses.value = await api.user.getAddresses() } catch (e) { console.error(e) }
  orderDialog.value = true
}

const submitOrder = async () => {
  const payload = {
    seckill_product_id: currentSp.value.id,
    quantity: qty.value,
    address_id: addrId.value
  }
  if (currentSku.value) {
    payload.sku_id = currentSku.value.sku_id
  }
  try {
    const r = await api.seckill.createOrder(payload)
    ElMessage.success('下单成功，请尽快支付')
    orderDialog.value = false
    router.push('/order/' + r.order_id)
  } catch (e) { console.error(e) }
}

onMounted(load)
onUnmounted(() => clearInterval(timer))
</script>

<style lang="scss" scoped>
.seckill-page { padding:20px; max-width:1100px; margin:0 auto; }
.seckill-header { display:flex; align-items:center; justify-content:space-between; padding:20px; background:linear-gradient(135deg,#ff4d4f,#ff7875); color:#fff; border-radius:8px; margin-bottom:20px; }
.countdown .time { font-size:24px; font-weight:bold; }
.product-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:20px; }
.seckill-item { background:#fff; border-radius:8px; overflow:hidden; border:1px solid #f0f0f0; }
.sp-image { height:200px; }
.sp-info { padding:15px; }
.sp-info h4 { font-size:14px; margin-bottom:10px; }
.seckill-price { font-size:20px; font-weight:bold; color:#ff4d4f; }
.orig-price { font-size:12px; color:#999; text-decoration:line-through; margin-left:8px; }
.sp-stock { color:#999; font-size:12px; margin:8px 0; }
.img-placeholder { width:100%; height:100%; display:flex; align-items:center; justify-content:center; background:#f5f5f5; color:#ccc; }
</style>
