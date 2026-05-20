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
    
    <el-dialog v-model="orderDialog" title="确认下单" width="450px">
      <el-form label-width="80px">
        <el-form-item label="商品">{{ currentSp?.product?.name }}</el-form-item>
        <el-form-item label="价格">¥{{ currentSp?.seckill_price }}</el-form-item>
        <el-form-item label="数量"><el-input-number v-model="qty" :min="1" :max="currentSp?.seckill_stock||1" /></el-form-item>
        <el-form-item label="地址"><el-select v-model="addrId" placeholder="选择收货地址"><el-option v-for="a in addresses" :key="a.address_id" :label="a.full_address" :value="a.address_id" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="orderDialog=false">取消</el-button><el-button type="danger" @click="submitOrder" :disabled="!addrId">确认下单</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
const router = useRouter()
const data = ref({ session: null, products: [] })
const countdown = ref('')
const orderDialog = ref(false), currentSp = ref(null), qty = ref(1), addrId = ref(null), addresses = ref([])
let timer = null

const load = async () => {
  try { data.value = await api.seckill.getCurrent(); if (data.value.session) startCountdown() } catch(e) { console.error(e) }
}
const startCountdown = () => {
  const tick = () => { const diff = new Date(data.value.session.end_time).getTime() - Date.now(); if (diff<=0) { countdown.value='已结束'; clearInterval(timer); return; } const h=Math.floor(diff/3600000), m=Math.floor((diff%3600000)/60000), s=Math.floor((diff%60000)/1000); countdown.value = h+':'+String(m).padStart(2,'0')+':'+String(s).padStart(2,'0') }
  tick(); timer = setInterval(tick, 1000)
}
const buy = async (sp) => { currentSp.value = sp; qty.value = 1; addrId.value = null; try { addresses.value = await api.user.getAddresses() } catch(e){console.error(e)} orderDialog.value = true }
const submitOrder = async () => {
  try { const r = await api.seckill.createOrder({ seckill_product_id: currentSp.value.id, quantity: qty.value, address_id: addrId.value }); ElMessage.success('下单成功，请尽快支付'); orderDialog.value = false; router.push('/order/' + r.order_id) } catch(e) { console.error(e) }
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
