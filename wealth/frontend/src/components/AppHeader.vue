<template>
  <header class="app-header">
    <div class="header-content">
      <div class="header-left">
        <router-link to="/" class="logo">
          <span class="logo-icon">📊</span>
          <span class="logo-text">{{ $t('app.name') }}</span>
        </router-link>
        <nav class="nav-menu">
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
            {{ $t('nav.home') }}
          </router-link>
          <router-link to="/stocks" class="nav-item" :class="{ active: $route.path.startsWith('/stocks') }">
            {{ $t('nav.stocks') }}
          </router-link>
          <router-link to="/funds" class="nav-item" :class="{ active: $route.path.startsWith('/funds') }">
            {{ $t('nav.funds') }}
          </router-link>
          <router-link to="/backtest" class="nav-item" :class="{ active: $route.path.startsWith('/backtest') }">
            {{ $t('nav.backtest') }}
          </router-link>
          <router-link to="/prediction" class="nav-item" :class="{ active: $route.path.startsWith('/prediction') }">
            {{ $t('nav.prediction') }}
          </router-link>
          <router-link to="/monitoring" class="nav-item" :class="{ active: $route.path.startsWith('/monitoring') }">
            {{ $t('nav.monitoring') }}
          </router-link>
        </nav>
      </div>
      <div class="header-right">
        <LanguageSwitcher />
      </div>
    </div>
  </header>
</template>

<script setup>
import LanguageSwitcher from './LanguageSwitcher.vue'
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(10, 14, 23, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--text-primary);
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  display: flex;
  gap: 4px;
}

.nav-item {
  padding: 8px 16px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  border-radius: var(--radius-sm);
  transition: var(--transition);
}

.nav-item:hover {
  color: var(--text-primary);
  background: var(--bg-card-hover);
}

.nav-item.active {
  color: var(--primary);
  background: rgba(102, 126, 234, 0.15);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }

  .header-content {
    padding: 0 16px;
  }
}
</style>
