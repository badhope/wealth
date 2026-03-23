import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/stocks',
      name: 'stocks',
      component: () => import('@/views/StocksView.vue')
    },
    {
      path: '/stocks/:symbol',
      name: 'stock-detail',
      component: () => import('@/views/StockDetailView.vue')
    },
    {
      path: '/funds',
      name: 'funds',
      component: () => import('@/views/FundsView.vue')
    },
    {
      path: '/backtest',
      name: 'backtest',
      component: () => import('@/views/BacktestView.vue')
    },
    {
      path: '/prediction',
      name: 'prediction',
      component: () => import('@/views/PredictionView.vue')
    },
    {
      path: '/alerts',
      name: 'alerts',
      component: () => import('@/views/AlertsView.vue')
    },
    {
      path: '/portfolio',
      name: 'portfolio',
      component: () => import('@/views/PortfolioView.vue')
    },
    {
      path: '/monitoring',
      name: 'monitoring',
      component: () => import('@/views/MonitoringView.vue')
    }
  ]
})

export default router
