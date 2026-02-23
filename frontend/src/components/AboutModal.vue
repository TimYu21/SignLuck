<template>
  <div class="modal-backdrop" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <button class="close-icon" @click="$emit('close')">×</button>
      
      <h2 class="modal-title">{{ t('about_title') }}</h2>
      
      <p class="dev-text">{{ t('about_dev') }}</p>

      <div class="logic-section">
        <h3 class="section-title">{{ t('about_logic_title') }}</h3>
        
        <div class="logic-block">
          <h4>{{ t('about_prob_title') }}</h4>
          <p>{{ t('about_prob_desc') }}</p>
        </div>

        <div class="logic-block">
          <h4>{{ t('about_route_title') }}</h4>
          <p>{{ t('about_route_desc') }}</p>
        </div>
      </div>

      <button class="action-btn" @click="$emit('close')">{{ t('close_btn') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTranslation } from '../composables/useTranslation';

const { t } = useTranslation();
defineEmits(['close']);
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(5px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-content {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 2rem;
  max-width: 600px;
  width: 100%;
  position: relative;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
  color: var(--text-main);
  font-family: 'Inter', sans-serif;
  max-height: 90vh;
  overflow-y: auto;
}

.close-icon {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  color: var(--text-dim);
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.close-icon:hover {
  color: var(--color-primary);
}

.modal-title {
  font-family: 'JetBrains Mono', monospace;
  color: var(--color-primary);
  margin-top: 0;
  margin-bottom: 1.5rem;
  text-align: center;
  font-size: 1.5rem;
}

.dev-text {
  color: var(--text-dim);
  margin-bottom: 2rem;
  font-size: 0.95rem;
  line-height: 1.6;
}

.section-title {
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-dim);
  font-size: 1rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 0.5rem;
}

.logic-block {
  margin-bottom: 1.5rem;
}

.logic-block h4 {
  color: var(--text-main);
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.logic-block p {
  color: var(--text-dim);
  font-size: 0.95rem;
  line-height: 1.6;
}

.action-btn {
  width: 100%;
  background: var(--color-primary);
  color: #000;
  border: none;
  padding: 0.8rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: bold;
  cursor: pointer;
  border-radius: 4px;
  margin-top: 1rem;
  transition: opacity 0.2s;
}

.action-btn:hover {
  opacity: 0.9;
}
</style>