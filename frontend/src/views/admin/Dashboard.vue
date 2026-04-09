<template>
  <div class="dashboard">
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-icon" style="background: #409eff">
          <el-icon :size="32"><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.total_users }}</div>
          <div class="stat-label">总用户数</div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-icon" style="background: #67c23a">
          <el-icon :size="32"><ShoppingCart /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.orders_today }}</div>
          <div class="stat-label">今日订单</div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-icon" style="background: #e6a23c">
          <el-icon :size="32"><Money /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">¥{{ stats.today_sales }}</div>
          <div class="stat-label">今日销售额</div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-icon" style="background: #f56c6c">
          <el-icon :size="32"><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">¥{{ stats.total_sales }}</div>
          <div class="stat-label">总销售额</div>
        </div>
      </el-card>
    </div>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>销售趋势</span>
          </template>
          <div ref="salesTrendChart" style="height: 400px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>热销商品 Top10</span>
          </template>
          <el-table :data="hotProducts" style="width: 100%">
            <el-table-column prop="product_id" label="ID" width="80" />
            <el-table-column prop="name" label="商品名称" />
            <el-table-column prop="sold_count" label="销量" width="100" />
            <el-table-column prop="price" label="价格" width="100">
              <template #default="{ row }">
                ¥{{ row.price }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { api } from '@/api'

const stats = ref({
  total_users: 0,
  orders_today: 0,
  today_sales: 0,
  total_sales: 0
})

const hotProducts = ref([])
const salesTrendChart = ref(null)

const loadStats = async () => {
  try {
    const data = await api.admin.getStatsOverview()
    stats.value = data

    const hotData = await api.admin.getHotProducts(10)
    hotProducts.value = hotData

    const trendData = await api.admin.getSalesTrend(7)
    renderSalesTrendChart(trendData)
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const renderSalesTrendChart = (data) => {
  if (!salesTrendChart.value) return

  const chart = echarts.init(salesTrendChart.value)

  chart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['销售额', '订单数']
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.date)
    },
    yAxis: [
      { type: 'value', name: '销售额', position: 'left' },
      { type: 'value', name: '订单数', position: 'right' }
    ],
    series: [
      {
        name: '销售额',
        type: 'line',
        smooth: true,
        data: data.map(item => item.sales_amount),
        itemStyle: { color: '#ff6700' }
      },
      {
        name: '订单数',
        type: 'bar',
        yAxisIndex: 1,
        data: data.map(item => item.order_count),
        itemStyle: { color: '#409eff' }
      }
    ]
  })
}

onMounted(() => {
  loadStats()
})
</script>

<style lang="scss" scoped>
.dashboard {
  padding: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;

  .stat-card {
    :deep(.el-card__body) {
      display: flex;
      align-items: center;
      padding: 20px;
    }

    .stat-icon {
      width: 64px;
      height: 64px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 20px;
      color: #fff;
    }

    .stat-content {
      flex: 1;

      .stat-value {
        font-size: 32px;
        font-weight: bold;
        color: #333;
      }

      .stat-label {
        font-size: 14px;
        color: #999;
        margin-top: 5px;
      }
    }
  }
}
</style>
