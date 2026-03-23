<template>
  <span :class="['tag', `tag-${type}`, `tag-${size}`]" :style="customStyle">
    <slot />
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'primary', 'success', 'warning', 'error', 'info'].includes(v)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (v) => ['small', 'medium', 'large'].includes(v)
  },
  color: {
    type: String,
    default: null
  }
})

const customStyle = computed(() => {
  if (props.color) {
    return {
      '--tag-color': props.color,
      backgroundColor: `${props.color}20`,
      color: props.color,
      borderColor: `${props.color}40`
    }
  }
  return {}
})
</script>

<style scoped>
.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 20px;
  border: 1px solid transparent;
  transition: var(--transition);
  white-space: nowrap;
}

.tag-small {
  padding: 2px 8px;
  font-size: 11px;
}

.tag-large {
  padding: 6px 14px;
  font-size: 14px;
}

.tag-default {
  background: var(--bg-card);
  color: var(--text-secondary);
  border-color: var(--border-color);
}

.tag-primary {
  background: rgba(102, 126, 234, 0.15);
  color: #667eea;
  border-color: rgba(102, 126, 234, 0.3);
}

.tag-success {
  background: rgba(38, 166, 154, 0.15);
  color: #26a69a;
  border-color: rgba(38, 166, 154, 0.3);
}

.tag-warning {
  background: rgba(255, 202, 40, 0.15);
  color: #ffca28;
  border-color: rgba(255, 202, 40, 0.3);
}

.tag-error {
  background: rgba(239, 83, 80, 0.15);
  color: #ef5350;
  border-color: rgba(239, 83, 80, 0.3);
}

.tag-info {
  background: rgba(0, 182, 214, 0.15);
  color: #00b6d6;
  border-color: rgba(0, 182, 214, 0.3);
}
</style>
