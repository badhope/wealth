<template>
  <div class="hover-card" :class="[`hover-card-${variant}`, { 'hover-card-clickable': clickable }]" @click="handleClick">
    <div class="hover-card-icon" v-if="icon">
      <span>{{ icon }}</span>
    </div>
    <div class="hover-card-content">
      <slot />
    </div>
    <div class="hover-card-indicator" v-if="indicator">
      <span :class="['indicator-dot', `indicator-${indicator}`]"></span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'primary', 'success', 'warning', 'error'].includes(v)
  },
  icon: {
    type: String,
    default: ''
  },
  clickable: {
    type: Boolean,
    default: false
  },
  indicator: {
    type: String,
    default: '',
    validator: (v) => ['', 'success', 'warning', 'error'].includes(v)
  }
})

const emit = defineEmits(['click'])

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.hover-card {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  transition: var(--transition);
  overflow: hidden;
}

.hover-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  opacity: 0;
  transition: var(--transition);
}

.hover-card:hover {
  background: var(--bg-card-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.hover-card:hover::before {
  opacity: 1;
}

.hover-card-clickable {
  cursor: pointer;
}

.hover-card-clickable:active {
  transform: translateY(0);
}

.hover-card-primary:hover {
  border-color: rgba(102, 126, 234, 0.3);
}

.hover-card-success:hover {
  border-color: rgba(38, 166, 154, 0.3);
}

.hover-card-warning:hover {
  border-color: rgba(255, 202, 40, 0.3);
}

.hover-card-error:hover {
  border-color: rgba(239, 83, 80, 0.3);
}

.hover-card-icon {
  font-size: 24px;
  opacity: 0.8;
}

.hover-card-content {
  flex: 1;
  min-width: 0;
}

.hover-card-indicator {
  position: absolute;
  top: 16px;
  right: 16px;
}

.indicator-dot {
  display: block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.indicator-success {
  background: var(--success);
  box-shadow: 0 0 8px var(--success);
}

.indicator-warning {
  background: var(--warning);
  box-shadow: 0 0 8px var(--warning);
}

.indicator-error {
  background: var(--error);
  box-shadow: 0 0 8px var(--error);
  animation: pulse-error 1.5s ease-in-out infinite;
}

@keyframes pulse-error {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
