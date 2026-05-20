<template>
  <div class="dashboard">
    <div class="stats-grid">
      <el-card class="stat-card"><div class="stat-icon" style="background:#409eff"><el-icon :size="32"><User /></el-icon></div><div class="stat-content"><div class="stat-value">{{ stats.total_users }}</div><div class="stat-label">总用户数</div></div></el-card>
      <el-card class="stat-card"><div class="stat-icon" style="background:#67c23a"><el-icon :size="32"><ShoppingCart /></el-icon></div><div class="stat-content"><div class="stat-value">{{ stats.orders_today }}</div><div class="stat-label">今日订单</div></div></el-card>
      <el-card class="stat-card"><div class="stat-icon" style="background:#e6a23c"><el-icon :size="32"><Money /></el-icon></div><div class="stat-content"><div class="stat-value">¥{{ stats.today_sales }}</div><div class="stat-label">今日销售额</div></div></el-card>
      <el-card class="stat-card"><div class="stat-icon" style="background:#f56c6c"><el-icon :size="32"><TrendCharts /></el-icon></div><div class="stat-content"><div class="stat-value">¥{{ stats.total_sales }}</div><div class="stat-label">总销售额</div></div></el-card>
    </div>

    <div class="chart-controls"><span>统计天数：</span><el-radio-group v-model="days" size="small" @change="onDaysChange"><el-radio-button :value="7">7天</el-radio-button><el-radio-button :value="30">30天</el-radio-button><el-radio-button :value="90">90天</el-radio-button></el-radio-group></div>

    <el-row :gutter="20">
      <el-col :span="16"><el-card><template #header><span>销售额与订单量趋势</span></template><div ref="salesChartEl" style="height:350px"></div></el-card></el-col>
      <el-col :span="8"><el-card><template #header><span>支付方式占比</span></template><div ref="sourceChartEl" style="height:350px"></div></el-card></el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="16"><el-card><template #header><span>商品销量排行</span></template><div ref="rankChartEl" style="height:350px"></div></el-card></el-col>
      <el-col :span="8"><el-card><template #header><span>用户增长趋势</span></template><div ref="growthChartEl" style="height:350px"></div></el-card></el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { api } from '@/api'

const stats = ref({ total_users:0, orders_today:0, today_sales:0, total_sales:0 })
const days = ref(7)
const salesChartEl = ref(null), sourceChartEl = ref(null), rankChartEl = ref(null), growthChartEl = ref(null)

const loadAll = async () => {
  try {
    stats.value = await api.admin.getStatsOverview()
    const [sc, pr, ug, os] = await Promise.all([
      api.admin.getSalesChart(days.value),
      api.admin.getProductRank(10),
      api.admin.getUserGrowth(days.value),
      api.admin.getOrderSource()
    ])
    renderSalesChart(sc)
    renderProductRank(pr)
    renderUserGrowth(ug)
    renderOrderSource(os)
  } catch (e) { console.error(e) }
}

const renderSalesChart = (d) => {
  if (!salesChartEl.value) return
  const c = echarts.init(salesChartEl.value)
  c.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['销售额', '订单量'] },
    xAxis: { type: 'category', data: d.dates },
    yAxis: [{ type: 'value', name: '销售额' }, { type: 'value', name: '订单量' }],
    series: [
      { name: '销售额', type: 'bar', data: d.amounts, itemStyle: { color: '#ff6700' } },
      { name: '订单量', type: 'line', smooth: true, yAxisIndex: 1, data: d.counts, itemStyle: { color: '#409eff' } }
    ]
  })
}

const renderProductRank = (d) => {
  if (!rankChartEl.value) return
  const c = echarts.init(rankChartEl.value)
  c.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '15%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: d.map(i=>i.name).reverse(), inverse: true },
    series: [{ type: 'bar', data: d.map(i=>i.qty).reverse(), itemStyle: { color: '#67c23a' }, label: { show: true, position: 'right' } }]
  })
}

const renderUserGrowth = (d) => {
  if (!growthChartEl.value) return
  const c = echarts.init(growthChartEl.value)
  c.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: d.dates },
    yAxis: { type: 'value' },
    series: [{ type: 'line', smooth: true, data: d.counts, areaStyle: { color: 'rgba(64,158,255,0.2)' }, itemStyle: { color: '#409eff' } }]
  })
}

const renderOrderSource = (d) => {
  if (!sourceChartEl.value) return
  const c = echarts.init(sourceChartEl.value)
  c.setOption({
    tooltip: { trigger: 'item' },
    series: [{ type: 'pie', radius: ['40%','70%'], data: d, label: { formatter: '{b}: {c}' } }]
  })
}

const onDaysChange = () => {
  api.admin.getSalesChart(days.value).then(renderSalesChart)
  api.admin.getUserGrowth(days.value).then(renderUserGrowth)
}

onMounted(loadAll)
</script>

<style lang="scss" scoped>
.dashboard { padding: 20px; }
.stats-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 20px; margin-bottom: 20px; }
.stat-card :deep(.el-card__body) { display: flex; align-items: center; padding: 20px; }
.stat-icon { width: 64px; height: 64px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 20px; color: #fff; }
.stat-value { font-size: 32px; font-weight: bold; color: #333; }
.stat-label { font-size: 14px; color: #999; margin-top: 5px; }
.chart-controls { margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
</style>
