<template>
  <Teleport to="body">
    <Transition name="backdrop">
      <div v-if="modelValue" class="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm flex items-center justify-center p-4" @click.self="$emit('update:modelValue', false)">
        <div class="w-full max-w-md rounded-2xl border border-gray-200 bg-white shadow-2xl overflow-hidden">
          <div class="flex items-center gap-3 border-b border-gray-100 px-4 py-3">
            <FeatherIcon name="search" class="h-4 w-4 text-gray-400 shrink-0" />
            <input
              ref="inputRef"
              v-model="query"
              type="text"
              :placeholder="`Search customer to add ${action}…`"
              class="flex-1 text-sm focus:outline-none bg-transparent"
              @input="onInput"
              @keydown.escape="$emit('update:modelValue', false)"
            />
            <button @click="$emit('update:modelValue', false)" class="text-gray-400 hover:text-gray-700">
              <FeatherIcon name="x" class="h-4 w-4" />
            </button>
          </div>

          <div class="max-h-72 overflow-y-auto">
            <div v-if="searching" class="flex items-center gap-2 px-4 py-3 text-sm text-gray-400">
              <FeatherIcon name="loader" class="h-3.5 w-3.5 animate-spin" /> Searching…
            </div>
            <div v-else-if="results.length">
              <button
                v-for="c in results" :key="c.name"
                class="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors border-b border-gray-50 last:border-0"
                @click="select(c)"
              >
                <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
                  {{ (c.customer_name || '?').charAt(0).toUpperCase() }}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">{{ c.customer_name }}</p>
                  <p class="text-xs text-gray-400 truncate">{{ [c.territory, c.customer_group].filter(Boolean).join(' · ') }}</p>
                </div>
                <FeatherIcon name="arrow-right" class="h-3.5 w-3.5 text-gray-300 shrink-0" />
              </button>
            </div>
            <div v-else-if="query.length > 1" class="px-4 py-6 text-center text-sm text-gray-400">
              No customers found for "{{ query }}"
            </div>
            <div v-else class="px-4 py-6 text-center text-sm text-gray-400">
              Type to search customers
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getList } from '@/utils/frappe'

const props = defineProps({
  modelValue: Boolean,
  action: { type: String, default: 'payment' }, // 'payment' or 'order'
})
const emit = defineEmits(['update:modelValue'])
const router = useRouter()

const query = ref('')
const results = ref([])
const searching = ref(false)
const inputRef = ref(null)
let searchTimer = null

watch(() => props.modelValue, async (val) => {
  if (val) {
    query.value = ''
    results.value = []
    await nextTick()
    inputRef.value?.focus()
  }
})

function onInput() {
  if (searchTimer) clearTimeout(searchTimer)
  if (query.value.length < 2) { results.value = []; return }
  searchTimer = setTimeout(doSearch, 300)
}

async function doSearch() {
  searching.value = true
  try {
    results.value = await getList('Customer', {
      fields: ['name', 'customer_name', 'territory', 'customer_group'],
      filters: { customer_name: ['like', `%${query.value}%`] },
      limit: 8,
    })
  } catch (e) { console.error(e) }
  finally { searching.value = false }
}

function select(customer) {
  emit('update:modelValue', false)
  // Navigate to customer detail and open the right tab
  router.push({
    path: `/customers/${customer.name}`,
    query: { tab: props.action === 'order' ? 'orders' : 'payments' }
  })
}
</script>

<style scoped>
.backdrop-enter-active, .backdrop-leave-active { transition: opacity 0.15s ease; }
.backdrop-enter-from, .backdrop-leave-to { opacity: 0; }
</style>
