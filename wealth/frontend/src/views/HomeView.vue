<template>
  <div class="home">
    <div class="hero">
      <h1>Wealth</h1>
      <p>智能量化分析平台</p>
    </div>
    <div class="stats">
      <div class="stat-card">
        <h3>A股市场</h3>
        <p class="value">{{ marketData.indices?.['000001']?.price || '--' }}</p>
        <p :class="marketData.indices?.['000001']?.change_pct >= 0 ? 'up' : 'down'">
          {{ marketData.indices?.['000001']?.change_pct >= 0 ? '+' : '' }}{{ marketData.indices?.['000001']?.change_pct || 0 }}%
        </p>
      </div>
      <div class="stat-card">
        <h3>涨跌幅</h3>
        <p class="up-count">{{ marketData.limit_up_count || 0 }}</p>
        <p>涨停</p>
      </div>
      <div class="stat-card">
        <h3>跌停</h3>
        <p class="down-count">{{ marketData.limit_down_count || 0 }}</p>
        <p>跌停</p>
      </div>
    </div>
    <div class="quick-actions">
      <router-link to="/stocks" class="action-btn">搜索股票</router-link>
      <router-link to="/backtest" class="action-btn">回测策略</router-link>
      <router-link to="/prediction" class="action-btn">价格预测</router-link>
      <router-link to="/alerts" class="action-btn">价格预警</router-link>
      <router-link to="/portfolio" class="action-btn">我的持仓</router-link>
      <router-link to="/monitoring" class="action-btn">系统监控</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marketApi } from '@/api'

const marketData = ref({})

onMounted(async () => {
  try {
    marketData.value = await marketApi.overview()
  } catch (e) {
    console.error(e)
  }
})
</script>

<style lang="scss" scoped>
.home {
  padding: 40px;
  color: #fff;
}
.hero {
  text-align: center;
  margin-bottom: 60px;
  h1 {
    font-size: 64px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 16px;
  }
  p {
    font-size: 24px;
    color: #888;
  }
}
.stats {
  display: flex;
  gap: 24px;
  justify-content: center;
  margin-bottom: 60px;
}
.stat-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  padding: 32px 48px;
  text-align: center;
  h3 { color: #888; font-size: 14px; margin-bottom: 8px; }
  .value { font-size: 32px; font-weight: bold; }
  .up { color: #ef5350; }
  .down { color: #26a69a; }
  .up-count { color: #ef5350; font-size: 32px; font-weight: bold; }
  .down-count { color: #26a69a; font-size: 32px; font-weight: bold; }
}
.quick-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}
.action-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 16px 32px;
  border-radius: 12px;
  text-decoration: none;
  font-size: 16px;
  transition: transform 0.2s;
  &:hover { transform: translateY(-2px); }
}
</style>
