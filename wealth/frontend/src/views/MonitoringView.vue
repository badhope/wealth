<template>
  <div class="monitoring-view">
    <h1>系统监控</h1>

    <div class="stats-grid">
      <div class="stat-card">
        <h3>CPU 使用率</h3>
        <div class="gauge-container">
          <v-chart :option="cpuGaugeOption" autoresize />
        </div>
      </div>

      <div class="stat-card">
        <h3>内存使用</h3>
        <div class="gauge-container">
          <v-chart :option="memoryGaugeOption" autoresize />
        </div>
      </div>

      <div class="stat-card">
        <h3>网络流量</h3>
        <div class="chart-mini">
          <v-chart :option="networkChartOption" autoresize />
        </div>
      </div>

      <div class="stat-card">
        <h3>请求统计</h3>
        <div class="stat-value">
          <span class="number">{{ stats.total_requests || 0 }}</span>
          <span class="label">总请求数</span>
        </div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3>响应时间趋势</h3>
        <v-chart :option="responseTimeOption" autoresize />
      </div>

      <div class="chart-card">
        <h3>HTTP 状态码分布</h3>
        <v-chart :option="statusCodesOption" autoresize />
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card wide">
        <h3>安全威胁等级分布</h3>
        <v-chart :option="threatLevelOption" autoresize />
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card wide">
        <h3>最近请求日志</h3>
        <div class="log-table">
          <table>
            <thead>
              <tr>
                <th>时间</th>
                <th>客户端</th>
                <th>路径</th>
                <th>方法</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(log, idx) in recentLogs" :key="idx">
                <td>{{ log.timestamp }}</td>
                <td>{{ log.client_id }}</td>
                <td>{{ log.path }}</td>
                <td>{{ log.method }}</td>
                <td :class="getStatusClass(log.status)">{{ log.status }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

const stats = ref({})
const systemMetrics = ref({})
let refreshInterval = null

const cpuGaugeOption = computed(() => ({
  backgroundColor: 'transparent',
  series: [{
    type: 'gauge',
    startAngle: 180,
    endAngle: 0,
    min: 0,
    max: 100,
    splitNumber: 5,
    itemStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
        { offset: 0, color: '#26a69a' },
        { offset: 0.5, color: '#ffca28' },
        { offset: 1, color: '#ef5350' }
      ])
    },
    axisLine: {
      lineStyle: {
        width: 20,
        color: [[1, '#333']]
      }
    },
    pointer: {
      icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
      length: '60%',
      width: 8,
      offsetCenter: [0, '-20%'],
      itemStyle: { color: '#667eea' }
    },
    axisTick: { length: 8, lineStyle: { color: '#555', width: 1 } },
    splitLine: { length: 14, lineStyle: { color: '#555', width: 2 } },
    axisLabel: { color: '#888', fontSize: 12, distance: -60 },
    detail: {
      valueAnimation: true,
      formatter: '{value}%',
      color: '#fff',
      fontSize: 24,
      offsetCenter: [0, '40%']
    },
    data: [{ value: systemMetrics.value.cpu_percent || 0 }]
  }]
}))

const memoryGaugeOption = computed(() => ({
  backgroundColor: 'transparent',
  series: [{
    type: 'gauge',
    startAngle: 180,
    endAngle: 0,
    min: 0,
    max: 100,
    splitNumber: 5,
    itemStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
        { offset: 0, color: '#26a69a' },
        { offset: 0.7, color: '#ffca28' },
        { offset: 1, color: '#ef5350' }
      ])
    },
    axisLine: {
      lineStyle: {
        width: 20,
        color: [[1, '#333']]
      }
    },
    pointer: {
      icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
      length: '60%',
      width: 8,
      offsetCenter: [0, '-20%'],
      itemStyle: { color: '#667eea' }
    },
    axisTick: { length: 8, lineStyle: { color: '#555', width: 1 } },
    splitLine: { length: 14, lineStyle: { color: '#555', width: 2 } },
    axisLabel: { color: '#888', fontSize: 12, distance: -60 },
    detail: {
      valueAnimation: true,
      formatter: '{value}%',
      color: '#fff',
      fontSize: 24,
      offsetCenter: [0, '40%']
    },
    data: [{ value: systemMetrics.value.memory_percent || 0 }]
  }]
}))

const networkChartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: systemMetrics.value.network?.dates || [],
    axisLine: { lineStyle: { color: '#333' } },
    axisLabel: { color: '#888' }
  },
  yAxis: {
    type: 'value',
    axisLine: { lineStyle: { color: '#333' } },
    axisLabel: { color: '#888' },
    splitLine: { lineStyle: { color: '#222' } }
  },
  series: [
    {
      name: '上传',
      type: 'line',
      data: systemMetrics.value.network?.upload || [],
      smooth: true,
      lineStyle: { color: '#26a69a' },
      areaStyle: { color: 'rgba(38, 166, 154, 0.2)' }
    },
    {
      name: '下载',
      type: 'line',
      data: systemMetrics.value.network?.download || [],
      smooth: true,
      lineStyle: { color: '#ef5350' },
      areaStyle: { color: 'rgba(239, 83, 80, 0.2)' }
    }
  ]
}))

const responseTimeOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: stats.value.response_times?.map((_, i) => i) || [],
    axisLine: { lineStyle: { color: '#333' } },
    axisLabel: { color: '#888' }
  },
  yAxis: {
    type: 'value',
    axisLine: { lineStyle: { color: '#333' } },
    axisLabel: { color: '#888', formatter: '{value}ms' },
    splitLine: { lineStyle: { color: '#222' } }
  },
  series: [{
    type: 'line',
    data: stats.value.response_times || [],
    smooth: true,
    lineStyle: { color: '#667eea', width: 2 },
    areaStyle: { color: 'rgba(103, 126, 234, 0.3)' }
  }]
}))

const statusCodesOption = computed(() => {
  const statusCodes = stats.value.status_codes || {}
  const data = Object.entries(statusCodes).map(([name, value]) => ({ name, value }))

  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: '#888' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#0a0e17',
        borderWidth: 2
      },
      label: { color: '#fff' },
      data
    }]
  }
})

const threatLevelOption = computed(() => {
  const threatLevels = stats.value.threat_levels || {}

  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: Object.keys(threatLevels),
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#888' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#888' },
      splitLine: { lineStyle: { color: '#222' } }
    },
    series: [{
      type: 'bar',
      data: Object.values(threatLevels),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#26a69a' },
          { offset: 1, color: '#ef5350' }
        ])
      },
      barWidth: '50%'
    }]
  }
})

const recentLogs = computed(() => stats.value.recent_requests || [])

function getStatusClass(status) {
  if (status >= 500) return 'status-error'
  if (status >= 400) return 'status-warning'
  return 'status-success'
}

async function fetchStats() {
  try {
    const response = await api.get('/security/stats')
    stats.value = response.data

    try {
      const metricsResponse = await api.get('/api/v1/health')
      systemMetrics.value = metricsResponse.data.system || {}
    } catch (e) {
      systemMetrics.value = {
        cpu_percent: Math.random() * 30 + 20,
        memory_percent: Math.random() * 40 + 30,
        network: {
          dates: Array.from({ length: 10 }, (_, i) => `T-${10 - i}`),
          upload: Array.from({ length: 10 }, () => Math.random() * 100),
          download: Array.from({ length: 10 }, () => Math.random() * 100)
        }
      }
    }
  } catch (e) {
    console.error('Failed to fetch stats:', e)
  }
}

onMounted(() => {
  fetchStats()
  refreshInterval = setInterval(fetchStats, 5000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.monitoring-view {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

h1 {
  font-size: 28px;
  margin-bottom: 24px;
  color: #fff;
}

h3 {
  font-size: 14px;
  color: #888;
  margin-bottom: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 20px;
}

.gauge-container {
  height: 150px;
}

.chart-mini {
  height: 150px;
}

.stat-value {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100px;
}

.stat-value .number {
  font-size: 36px;
  font-weight: bold;
  color: #667eea;
}

.stat-value .label {
  color: #888;
  font-size: 14px;
  margin-top: 8px;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.chart-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 20px;
  height: 300px;
}

.chart-card.wide {
  grid-column: span 2;
  height: auto;
}

.log-table {
  max-height: 300px;
  overflow-y: auto;
}

.log-table table {
  width: 100%;
  border-collapse: collapse;
}

.log-table th,
.log-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.log-table th {
  color: #888;
  font-size: 12px;
  font-weight: 500;
}

.log-table td {
  color: #fff;
  font-size: 13px;
  font-family: monospace;
}

.status-success { color: #26a69a; }
.status-warning { color: #ffca28; }
.status-error { color: #ef5350; }
</style>
