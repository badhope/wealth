<template>
  <div class="prediction-view">
    <h1>价格预测</h1>

    <div class="config-panel">
      <div class="form-row">
        <label>股票代码</label>
        <input v-model="symbol" placeholder="如: 000001" />
      </div>
      <div class="form-row">
        <label>预测模型</label>
        <select v-model="selectedModel">
          <option value="ensemble">集成模型 (Ensemble)</option>
          <option value="lstm">LSTM 深度学习</option>
          <option value="prophet">Prophet 时间序列</option>
          <option value="xgboost">XGBoost 梯度提升</option>
        </select>
      </div>
      <div class="form-row">
        <label>预测天数</label>
        <input v-model="predictionDays" type="number" min="5" max="90" />
      </div>
      <button class="run-btn" @click="runPrediction" :disabled="loading">
        {{ loading ? '预测中...' : '运行预测' }}
      </button>
    </div>

    <div v-if="result" class="results">
      <div class="prediction-chart">
        <h3>价格预测</h3>
        <v-chart :option="predictionChartOption" autoresize />
      </div>

      <div class="metrics-panel">
        <h3>模型性能</h3>
        <div class="metric-grid">
          <div class="metric">
            <span class="label">R² 分数</span>
            <span class="value">{{ result.metrics.r2?.toFixed(4) || '--' }}</span>
          </div>
          <div class="metric">
            <span class="label">RMSE</span>
            <span class="value">{{ result.metrics.rmse?.toFixed(4) || '--' }}</span>
          </div>
          <div class="metric">
            <span class="label">MAE</span>
            <span class="value">{{ result.metrics.mae?.toFixed(4) || '--' }}</span>
          </div>
          <div class="metric">
            <span class="label">MAPE</span>
            <span class="value">{{ result.metrics.mape?.toFixed(2) || '--' }}%</span>
          </div>
        </div>
      </div>

      <div v-if="result.feature_importance" class="feature-importance">
        <h3>特征重要性</h3>
        <v-chart :option="featureImportanceOption" autoresize />
      </div>

      <div class="confidence-interval">
        <h3>预测置信区间</h3>
        <div class="interval-stats">
          <div class="stat">
            <span class="label">当前价格</span>
            <span class="value">{{ result.currentPrice?.toFixed(2) || '--' }}</span>
          </div>
          <div class="stat">
            <span class="label">30天后预测</span>
            <span class="value up">{{ result.predictedPrice?.toFixed(2) || '--' }}</span>
          </div>
          <div class="stat">
            <span class="label">预测涨幅</span>
            <span :class="result.change >= 0 ? 'value up' : 'value down'">
              {{ result.change >= 0 ? '+' : '' }}{{ result.change?.toFixed(2) || '--' }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/api'

const symbol = ref('')
const selectedModel = ref('ensemble')
const predictionDays = ref(30)
const loading = ref(false)
const result = ref(null)
const error = ref('')

const predictionChartOption = computed(() => {
  if (!result.value?.chartData) return {}

  return {
    backgroundColor: '#0a0e17',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['历史数据', '预测', '置信区间'],
      textStyle: { color: '#fff' }
    },
    xAxis: {
      type: 'category',
      data: result.value.chartData.dates,
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
        name: '历史数据',
        type: 'line',
        data: result.value.chartData.historical,
        smooth: true,
        lineStyle: { color: '#667eea', width: 2 },
        itemStyle: { color: '#667eea' }
      },
      {
        name: '预测',
        type: 'line',
        data: result.value.chartData.predicted,
        smooth: true,
        lineStyle: { color: '#ef5350', width: 2, type: 'dashed' },
        itemStyle: { color: '#ef5350' }
      },
      {
        name: '置信区间',
        type: 'line',
        data: result.value.chartData.upper,
        smooth: true,
        lineStyle: { opacity: 0 },
        areaStyle: {
          color: 'rgba(103, 126, 234, 0.2)',
          opacity: 0.3
        }
      },
      {
        name: '置信区间',
        type: 'line',
        data: result.value.chartData.lower,
        smooth: true,
        lineStyle: { opacity: 0 }
      }
    ]
  }
})

const featureImportanceOption = computed(() => {
  if (!result.value?.feature_importance) return {}

  const data = result.value.feature_importance.sort((a, b) => b.importance - a.importance)

  return {
    backgroundColor: '#0a0e17',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#888' }
    },
    yAxis: {
      type: 'category',
      data: data.map(d => d.feature),
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#888' }
    },
    series: [{
      type: 'bar',
      data: data.map(d => d.importance),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ])
      }
    }]
  }
})

async function runPrediction() {
  if (!symbol.value) {
    error.value = '请输入股票代码'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await api.post('/prediction', {
      symbol: symbol.value,
      model: selectedModel.value,
      days: predictionDays.value
    })
    result.value = response.data
  } catch (e) {
    error.value = e.response?.data?.detail || '预测失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.prediction-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

h1 {
  font-size: 28px;
  margin-bottom: 24px;
  color: #fff;
}

h3 {
  font-size: 16px;
  color: #888;
  margin-bottom: 12px;
}

.config-panel {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.form-row label {
  width: 100px;
  color: #888;
}

.form-row input,
.form-row select {
  flex: 1;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
}

.run-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.run-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.run-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.results {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.prediction-chart,
.feature-importance {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  height: 400px;
}

.metrics-panel {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.metric {
  background: rgba(255, 255, 255, 0.05);
  padding: 16px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric .label {
  color: #888;
  font-size: 12px;
}

.metric .value {
  font-size: 20px;
  color: #fff;
}

.confidence-interval {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
}

.interval-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat {
  background: rgba(255, 255, 255, 0.05);
  padding: 16px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat .label {
  color: #888;
  font-size: 12px;
}

.stat .value {
  font-size: 24px;
  font-weight: bold;
}

.stat .value.up { color: #ef5350; }
.stat .value.down { color: #26a69a; }

.error {
  background: rgba(244, 67, 54, 0.2);
  border: 1px solid #f44336;
  border-radius: 8px;
  padding: 16px;
  color: #f44336;
  margin-top: 16px;
}
</style>
