<template>
  <div class="relative inline-flex items-center gap-2" ref="root">
    <button type="button"
      class="flex h-9 items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-700 hover:bg-gray-50 focus:outline-none"
      @click="menuOpen = !menuOpen">
      <FeatherIcon name="calendar" class="h-3.5 w-3.5 text-gray-400" />
      <span>{{ activeLabel }}</span>
      <FeatherIcon name="chevron-down" class="h-3.5 w-3.5 text-gray-400" />
    </button>

    <template v-if="preset === 'custom'">
      <input :value="from" type="date" @change="onCustom('from', $event.target.value)"
        class="h-9 rounded-md border bg-white px-2 text-sm focus:outline-none"
        :class="error ? 'border-red-300' : 'border-gray-200'" />
      <span class="text-xs text-gray-400">to</span>
      <input :value="to" type="date" :min="from" @change="onCustom('to', $event.target.value)"
        class="h-9 rounded-md border bg-white px-2 text-sm focus:outline-none"
        :class="error ? 'border-red-300' : 'border-gray-200'" />
    </template>

    <span v-if="error" class="text-xs text-red-500">{{ error }}</span>

    <div v-if="menuOpen"
      class="absolute top-10 left-0 z-30 w-44 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
      <button v-for="opt in presetOptions" :key="opt.id"
        type="button"
        class="flex w-full items-center gap-2 px-3 py-1.5 text-left text-sm hover:bg-gray-50"
        :class="preset === opt.id ? 'text-gray-900 font-medium' : 'text-gray-600'"
        @click="selectPreset(opt.id)">
        <FeatherIcon v-if="preset === opt.id" name="check" class="h-3.5 w-3.5 text-blue-500" />
        <span v-else class="w-3.5" />
        {{ opt.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import dayjs from 'dayjs'
import quarterOfYear from 'dayjs/plugin/quarterOfYear'

// dayjs has no built-in concept of quarters; without this plugin
// startOf('quarter') silently returns the start of TODAY, and
// add(N, 'quarter') is a no-op. Both This Quarter and Last Quarter
// would then collapse to "today → today". Extending fixes both.
dayjs.extend(quarterOfYear)

const props = defineProps({
  from: { type: String, default: '' },
  to: { type: String, default: '' },
  defaultPreset: { type: String, default: '' },
  allowAllTime: { type: Boolean, default: true },
  // "This X" presets (this_week / this_month / this_quarter / this_year)
  // default to start-of-period → today (i.e. "to-date"), which suits
  // backward-looking lists like Orders or Payments. For lists that span
  // future dates (HR leaves, beat schedules, planned visits), pass
  // forward-looking="true" so they cover the FULL period instead.
  forwardLooking: { type: Boolean, default: false },
})
const emit = defineEmits(['update:from', 'update:to', 'change'])

const root = ref(null)
const menuOpen = ref(false)
const preset = ref(props.defaultPreset || (props.allowAllTime ? '' : 'this_month'))
const error = ref('')

// "This X" range end: today for backward-looking lists, end-of-period
// for forward-looking ones. Implementation note: we wrap in a getter so
// the prop is re-read each call (otherwise the closure captures the
// initial value).
function thisEnd(unit) {
  return props.forwardLooking ? endOf(unit) : today()
}

const PRESETS = {
  '':            { label: 'All time',     range: () => [null, null] },
  today:         { label: 'Today',        range: () => [d(0), d(0)] },
  yesterday:     { label: 'Yesterday',    range: () => [d(-1), d(-1)] },
  this_week:     { label: 'This Week',    range: () => [startOf('week'), thisEnd('week')] },
  last_week:     { label: 'Last Week',    range: () => [startOf('week', -1, 'week'), endOf('week', -1, 'week')] },
  this_month:    { label: 'This Month',   range: () => [startOf('month'), thisEnd('month')] },
  last_month:    { label: 'Last Month',   range: () => [startOf('month', -1, 'month'), endOf('month', -1, 'month')] },
  this_quarter:  { label: 'This Quarter', range: () => [startOf('quarter'), thisEnd('quarter')] },
  last_quarter:  { label: 'Last Quarter', range: () => [startOf('quarter', -1, 'quarter'), endOf('quarter', -1, 'quarter')] },
  this_year:     { label: 'This Year',    range: () => [startOf('year'), thisEnd('year')] },
  custom:        { label: 'Custom Range…', range: () => [props.from || null, props.to || null] },
}

function d(offset) { return dayjs().add(offset, 'day').format('YYYY-MM-DD') }
function today() { return dayjs().format('YYYY-MM-DD') }
// IMPORTANT: original code did `dayjs().add(offset, unit).startOf(unit)` which
// passed the unit as both the add-unit and the startOf-unit. Fine for offset=0,
// but for "last week", calling startOf with the OUTER unit was correct only
// because add unit == startOf unit. Keep that pattern but make it explicit so
// the call signature reads cleanly.
function startOf(unit, offset = 0, addUnit = unit) {
  return dayjs().add(offset, addUnit).startOf(unit).format('YYYY-MM-DD')
}
function endOf(unit, offset = 0, addUnit = unit) {
  return dayjs().add(offset, addUnit).endOf(unit).format('YYYY-MM-DD')
}

const presetOptions = computed(() =>
  Object.entries(PRESETS)
    .filter(([id]) => id !== '' || props.allowAllTime)
    .map(([id, v]) => ({ id, label: v.label }))
)

const activeLabel = computed(() => PRESETS[preset.value]?.label || 'All time')

function validate(f, t) {
  if (f && t && dayjs(t).isBefore(dayjs(f))) { error.value = 'End before start'; return false }
  if (f && t && dayjs(t).diff(dayjs(f), 'day') > 366) { error.value = 'Range exceeds 1 year'; return false }
  error.value = ''
  return true
}

function emitRange(f, t) {
  emit('update:from', f || '')
  emit('update:to', t || '')
  emit('change', { from: f || null, to: t || null })
}

function selectPreset(id) {
  preset.value = id
  menuOpen.value = false
  if (id === 'custom') { error.value = ''; return }
  const [f, t] = PRESETS[id].range()
  validate(f, t)
  emitRange(f, t)
}

function onCustom(which, val) {
  let f = props.from, t = props.to
  if (which === 'from') f = val
  else t = val
  if (!validate(f, t)) {
    emit('update:from', f || '')
    emit('update:to', t || '')
    return
  }
  emitRange(f, t)
}

function onDocClick(e) {
  if (root.value && !root.value.contains(e.target)) menuOpen.value = false
}
onMounted(() => {
  document.addEventListener('click', onDocClick)
  if (preset.value && preset.value !== 'custom') {
    const [f, t] = PRESETS[preset.value].range()
    emitRange(f, t)
  }
})
onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
</script>
