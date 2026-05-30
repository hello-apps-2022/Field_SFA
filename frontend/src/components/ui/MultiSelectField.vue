<template>
  <div ref="root">
    <label v-if="label" class="mb-1 block text-xs font-medium text-gray-600">{{ label }}</label>
    <div class="rounded-md border bg-white px-2 py-1.5 focus-within:border-gray-400"
      :class="error ? 'border-red-400' : 'border-gray-300'">
      <div v-if="selected.length" class="mb-1 flex flex-wrap gap-1">
        <span v-for="v in selected" :key="v"
          class="inline-flex items-center gap-1 rounded bg-gray-900 px-2 py-0.5 text-xs font-medium text-white">
          {{ labelFor(v) }}
          <button type="button" class="hover:text-gray-300" @click="remove(v)">
            <FeatherIcon name="x" class="h-3 w-3" />
          </button>
        </span>
      </div>
      <div class="relative">
        <input v-model="query" @focus="open = true" @input="open = true"
          :placeholder="selected.length ? 'Add more…' : (placeholder || 'Search…')"
          class="w-full bg-transparent text-sm outline-none placeholder-gray-400" />
        <div v-if="open && filtered.length"
          class="absolute z-30 mt-1 max-h-52 w-full overflow-auto rounded-md border border-gray-200 bg-white shadow-lg">
          <button v-for="o in filtered" :key="o.value" type="button"
            class="block w-full px-3 py-1.5 text-left text-sm text-gray-700 hover:bg-gray-50"
            @click="add(o.value)">{{ o.label }}</button>
        </div>
        <div v-else-if="open && query && !filtered.length"
          class="absolute z-30 mt-1 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-xs text-gray-400 shadow-lg">
          No matches
        </div>
      </div>
    </div>
    <p v-if="error" class="mt-1 text-xs text-red-500">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  options: { type: Array, default: () => [] },
  label: String, placeholder: String, error: String,
})
const emit = defineEmits(['update:modelValue'])

const root = ref(null)
const query = ref('')
const open = ref(false)
const selected = computed(() => props.modelValue || [])

function labelFor(v) {
  const o = props.options.find(x => x.value === v)
  return o ? o.label : v
}
const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return props.options
    .filter(o => !selected.value.includes(o.value))
    .filter(o => !q || (o.label || '').toLowerCase().includes(q) || (o.value || '').toLowerCase().includes(q))
    .slice(0, 50)
})
function add(v) {
  if (!selected.value.includes(v)) emit('update:modelValue', [...selected.value, v])
  query.value = ''
}
function remove(v) { emit('update:modelValue', selected.value.filter(x => x !== v)) }

function onDocClick(e) { if (root.value && !root.value.contains(e.target)) open.value = false }
onMounted(() => document.addEventListener('mousedown', onDocClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', onDocClick))
</script>
