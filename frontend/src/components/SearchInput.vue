<template>
  <div class="search-field">
    <div class="input-prefix">{{ t('search_label') }}</div>
    <input
      ref="inputRef"
      :value="modelValue"
      @input="updateValue"
      type="text"
      :placeholder="t('search_placeholder')"
      class="main-input"
      spellcheck="false"
      autocomplete="off"
    />
    <button v-if="modelValue" class="input-suffix" @click="$emit('clear')">
      {{ t('search_clear') }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useTranslation } from '../composables/useTranslation';

defineProps<{ modelValue: string, loading?: boolean }>();
const emit = defineEmits(['update:modelValue', 'clear']);

const inputRef = ref<HTMLInputElement | null>(null);
const { t } = useTranslation();

const updateValue = (e: Event) => {
  emit('update:modelValue', (e.target as HTMLInputElement).value.toUpperCase());
};

onMounted(() => {
  inputRef.value?.focus();
});
</script>

<style scoped>
.search-field {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  display: flex;
  align-items: center;
  padding: 0 1rem;
  height: 56px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s ease;
}

.search-field:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-dim);
}

.input-prefix {
  color: var(--text-dim);
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  margin-right: 1rem;
  font-size: 0.8rem;
  text-transform: uppercase;
  min-width: 4.5rem;
  text-align: right;
}

.main-input {
  background: transparent;
  border: none;
  color: var(--text-main);
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.2rem;
  font-weight: 500;
  width: 100%;
  outline: none;
  text-transform: uppercase;
  flex: 1;
}

.main-input::placeholder {
  color: var(--text-dim);
}

.input-suffix {
  background: none;
  border: none;
  color: var(--color-primary);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  transition: color 0.2s;
  padding: 4px 8px;
  border-radius: 4px;
}

.input-suffix:hover {
  background: var(--color-primary-dim);
}

@media (max-width: 640px) {
  .search-field {
    height: 52px;
  }

  .main-input {
    font-size: 1.1rem;
  }
}
</style>
