<template>
  <div class="stats-page">
    <div class="page-header">
      <h2>消费统计</h2>
      <el-button @click="exportToExcel" :loading="exporting">
        <el-icon><Download /></el-icon>
        导出 Excel
      </el-button>
    </div>
    
    <!-- 时间范围选择 -->
    <el-card class="filter-card">
      <el-radio-group v-model="dateRange" @change="handleDateRangeChange">
        <el-radio-button label="7">最近7天</el-radio-button>
        <el-radio-button label="30">最近30天</el-radio-button>
        <el-radio-button label="90">最近3个月</el-radio-button>
        <el-radio-button label="custom">自定义</el-radio-button>
      </el-radio-group>
      
      <el-date-picker
        v-if="dateRange === 'custom'"
        v-model="customDateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        @change="handleCustomDateChange"
      />
    </el-card>
    
    <!-- 总体统计 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-icon orders">
            <el-icon :size="32"><ShoppingBag /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalStats.total_orders }}</div>
            <div class="stat-label">订单数量</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-icon amount">
            <el-icon :size="32"><Money /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">¥{{ totalStats.total_amount.toFixed(2) }}</div>
            <div class="stat-label">总消费</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-icon avg">
            <el-icon :size="32"><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">¥{{ avgAmount.toFixed(2) }}</div>
            <div class="stat-label">平均消费</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 消费趋势图 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>消费趋势</span>
          <el-radio-group v-model="chartPeriod" size="small">
            <el-radio-button label="daily">按日</el-radio-button>
            <el-radio-button label="weekly">按周</el-radio-button>
            <el-radio-button label="monthly">按月</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="trendChart" class="chart" style="height: 400px"></div>
    </el-card>
    
    <!-- 消费分类占比 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>消费分类占比</span>
          </template>
          <div ref="categoryChart" class="chart" style="height: 350px"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>消费详情</span>
          </template>
          <el-table :data="categoryDistribution" height="350">
            <el-table-column prop="name" label="分类" />
            <el-table-column prop="value" label="金额">
              <template #default="{ row }">
                ¥{{ row.value.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="占比">
              <template #default="{ row }">
                {{ ((row.value / totalStats.total_amount) * 100).toFixed(1) }}%
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { saveAs } from 'file-saver'
import * as XLSX from 'xlsx'

const dateRange = ref('30')
const customDateRange = ref([])
const chartPeriod = ref('daily')
const exporting = ref(false)

const totalStats = ref({
  total_orders: 0,
  total_amount: 0
})

const trendData = ref([])
const categoryDistribution = ref([])

const trendChart = ref(null)
const categoryChart = ref(null)
let trendChartInstance = null
let categoryChartInstance = null

const avgAmount = computed(() => {
  if (totalStats.value.total_orders === 0) return 0
  return totalStats.value.total_amount / totalStats.value.total_orders
})

const loadStats = async () => {
  let startDate, endDate
  
  if (dateRange.value === 'custom') {
    if (customDateRange.value && customDateRange.value.length === 2) {
      startDate = dayjs(customDateRange.value[0]).format('YYYY-MM-DD')
      endDate = dayjs(customDateRange.value[1]).format('YYYY-MM-DD')
    } else {
      return
    }
  } else {
    const days = parseInt(dateRange.value)
    endDate = dayjs().format('YYYY-MM-DD')
    startDate = dayjs().subtract(days, 'day').format('YYYY-MM-DD')
  }
  
  try {
    const data = await api.user.getConsumptionStats({
      start_date: startDate,
      end_date: endDate,
      period: chartPeriod.value
    })
    
    totalStats.value = data.total_stats
    trendData.value = data.trend
    categoryDistribution.value = data.category_distribution
    
    renderCharts()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const renderCharts = () => {
  renderTrendChart()
  renderCategoryChart()
}

const renderTrendChart = () => {
  if (!trendChart.value) return
  
  if (!trendChartInstance) {
    trendChartInstance = echarts.init(trendChart.value)
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['消费金额', '订单数量']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trendData.value.map(item => item.date)
    },
    yAxis: [
      {
        type: 'value',
        name: '消费金额',
        axisLabel: {
          formatter: '¥{value}'
        }
      },
      {
        type: 'value',
        name: '订单数量',
        position: 'right'
      }
    ],
    series: [
      {
        name: '消费金额',
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 103, 0, 0.3)' },
            { offset: 1, color: 'rgba(255, 103, 0, 0.05)' }
          ])
        },
        lineStyle: {
          color: '#ff6700',
          width: 3
        },
        itemStyle: {
          color: '#ff6700'
        },
        data: trendData.value.map(item => item.amount)
      },
      {
        name: '订单数量',
        type: 'bar',
        yAxisIndex: 1,
        itemStyle: {
          color: '#409eff'
        },
        data: trendData.value.map(item => item.order_count)
      }
    ]
  }
  
  trendChartInstance.setOption(option)
}

const renderCategoryChart = () => {
  if (!categoryChart.value) return
  
  if (!categoryChartInstance) {
    categoryChartInstance = echarts.init(categoryChart.value)
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '消费分类',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: categoryDistribution.value.map((item, index) => ({
          ...item,
          itemStyle: {
            color: ['#ff6700', '#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399'][index % 6]
          }
        }))
      }
    ]
  }
  
  categoryChartInstance.setOption(option)
}

const handleDateRangeChange = () => {
  if (dateRange.value !== 'custom') {
    loadStats()
  }
}

const handleCustomDateChange = () => {
  if (customDateRange.value && customDateRange.value.length === 2) {
    loadStats()
  }
}

const exportToExcel = async () => {
  exporting.value = true
  
  try {
    // 准备数据
    const excelData = [
      ['日期', '消费金额', '订单数量'],
      ...trendData.value.map(item => [
        item.date,
        item.amount.toFixed(2),
        item.order_count
      ])
    ]
    
    const ws = XLSX.utils.aoa_to_sheet(excelData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '消费统计')
    
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([wbout], { type: 'application/octet-stream' })
    
    const fileName = `消费统计_${dayjs().format('YYYY-MM-DD')}.xlsx`
    saveAs(blob, fileName)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

watch(chartPeriod, () => {
  loadStats()
})

onMounted(() => {
  loadStats()
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    trendChartInstance?.resize()
    categoryChartInstance?.resize()
  })
})
</script>

<style lang="scss" scoped>
.stats-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  h2 {
    margin: 0;
  }
}

.filter-card {
  margin-bottom: 20px;
}

.stats-cards {
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
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 20px;
      color: #fff;
      
      &.orders {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
      
      &.amount {
        background: linear-gradient(135deg, #ff6700 0%, #ff8533 100%);
      }
      
      &.avg {
        background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
      }
    }
    
    .stat-content {
      .stat-value {
        font-size: 28px;
        font-weight: bold;
        color: #333;
        margin-bottom: 5px;
      }
      
      .stat-label {
        font-size: 14px;
        color: #999;
      }
    }
  }
}

.chart-card {
  margin-bottom: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .chart {
    width: 100%;
  }
}
</style>
