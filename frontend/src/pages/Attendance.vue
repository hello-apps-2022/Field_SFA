<template>
  <div class="flex h-full flex-col overflow-hidden">
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <h1 class="text-sm font-semibold text-gray-900">Attendance</h1>
      <div class="flex-1" />
      <span v-if="streak > 0" class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
        🔥 {{ streak }}-day streak
      </span>
      <span class="text-xs text-gray-400">{{ todayLabel }}</span>
    </div>

    <div class="flex-1 overflow-auto p-5">
      <div class="mx-auto max-w-md">
        <!-- Greeting -->
        <div class="mb-4 text-center">
          <p class="text-lg font-semibold text-gray-900">{{ greeting }}<span v-if="firstName">, {{ firstName }}</span></p>
          <p class="text-xs text-gray-500">{{ subGreeting }}</p>
        </div>

        <!-- NOT STARTED: plan + start -->
        <div v-if="status === 'not_started'" class="rounded-xl border border-gray-200 bg-white p-5">
          <p class="text-sm font-medium text-gray-900">What's your focus today?</p>
          <p class="mb-2.5 text-xs text-gray-400">Tap what you'll work on.</p>
          <div class="mb-4 flex flex-wrap gap-2">
            <button v-for="opt in focusOptions" :key="opt" type="button" @click="toggleFocus(opt)"
              class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
              :class="selectedFocus.includes(opt) ? 'border-gray-900 bg-gray-900 text-white' : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'">
              {{ opt }}
            </button>
          </div>

          <p class="text-sm font-medium text-gray-900">Top priorities</p>
          <p class="mb-2.5 text-xs text-gray-400">Optional — a quick plan before you head out.</p>
          <div class="space-y-2">
            <div v-for="(p, i) in priorityInputs" :key="i" class="flex items-center gap-2">
              <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-medium text-gray-500">{{ i + 1 }}</span>
              <input v-model="priorityInputs[i]" :placeholder="placeholders[i]"
                class="h-9 flex-1 rounded-md border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none" />
            </div>
          </div>

          <button
            class="mt-4 inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-gray-900 px-4 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50"
            :disabled="busy" @click="mark('IN')">
            <FeatherIcon :name="busy ? 'loader' : 'sunrise'" class="h-4 w-4" :class="busy ? 'animate-spin' : ''" />
            {{ busy ? 'Getting location…' : 'Start Day' }}
          </button>
          <p v-if="geoNote" class="mt-2 text-center text-[11px] text-gray-400">{{ geoNote }}</p>
        </div>

        <!-- CHECKED IN: on the clock + focus list -->
        <div v-else-if="status === 'checked_in'" class="rounded-xl border border-green-200 bg-green-50/40 p-5">
          <div class="flex items-center gap-3">
            <span class="flex h-11 w-11 items-center justify-center rounded-full bg-green-100 text-green-600">
              <FeatherIcon name="check-circle" class="h-6 w-6" />
            </span>
            <div>
              <p class="text-sm font-semibold text-gray-900">Your day is underway</p>
              <p class="text-xs text-gray-500">Started {{ fmtTime(todayState.first_in && todayState.first_in.time) }}</p>
            </div>
          </div>

          <div v-if="focusList.length" class="mt-4 flex flex-wrap gap-1.5">
            <span v-for="f in focusList" :key="f" class="rounded-full bg-white border border-gray-200 px-2.5 py-1 text-xs text-gray-600">{{ f }}</span>
          </div>

          <div v-if="priorityList.length" class="mt-4">
            <p class="mb-1.5 text-[10px] font-semibold uppercase tracking-wide text-gray-400">Today's priorities</p>
            <ul class="space-y-1.5">
              <li v-for="(p, i) in priorityList" :key="i" class="flex items-start gap-2 text-sm text-gray-700">
                <FeatherIcon name="target" class="mt-0.5 h-3.5 w-3.5 shrink-0 text-gray-400" />
                <span>{{ p }}</span>
              </li>
            </ul>
          </div>

          <button
            class="mt-5 inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-white px-4 text-sm font-medium text-gray-700 border border-gray-300 hover:bg-gray-50 disabled:opacity-50"
            :disabled="busy" @click="mark('OUT')">
            <FeatherIcon :name="busy ? 'loader' : 'sunset'" class="h-4 w-4" :class="busy ? 'animate-spin' : ''" />
            {{ busy ? 'Getting location…' : 'End Day' }}
          </button>
          <p v-if="geoNote" class="mt-2 text-center text-[11px] text-gray-400">{{ geoNote }}</p>
        </div>

        <!-- CHECKED OUT: wrapped, with option to resume -->
        <div v-else class="rounded-xl border border-gray-200 bg-white p-5 text-center">
          <span class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 text-gray-500">
            <FeatherIcon name="moon" class="h-6 w-6" />
          </span>
          <p class="text-sm font-semibold text-gray-900">Day wrapped — nice work 🎉</p>
          <p class="mt-1 text-xs text-gray-500">
            {{ fmtTime(todayState.first_in && todayState.first_in.time) }}
            <template v-if="todayState.last_out"> → {{ fmtTime(todayState.last_out.time) }}</template>
            <template v-if="todayState.worked_hours"> · {{ todayState.worked_hours }}h worked</template>
          </p>
          <button
            class="mt-4 inline-flex h-10 items-center justify-center gap-2 rounded-md border border-gray-300 bg-white px-4 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            :disabled="busy" @click="mark('IN')">
            <FeatherIcon :name="busy ? 'loader' : 'rotate-cw'" class="h-4 w-4" :class="busy ? 'animate-spin' : ''" />
            {{ busy ? 'Getting location…' : 'Start Day again' }}
          </button>
          <p class="mt-2 text-[11px] text-gray-400">Back from a break? Pick up where you left off.</p>
          <p v-if="geoNote" class="mt-2 text-[11px] text-gray-400">{{ geoNote }}</p>
        </div>

        <!-- Today's log -->
        <div v-if="todayState.logs && todayState.logs.length" class="mt-5">
          <p class="mb-2 text-[10px] font-semibold uppercase tracking-wide text-gray-400">Today's log</p>
          <ul class="divide-y divide-gray-100 rounded-lg border border-gray-200 bg-white">
            <li v-for="l in todayState.logs" :key="l.name" class="flex items-center gap-3 px-4 py-2.5 text-sm">
              <FeatherIcon :name="l.log_type === 'IN' ? 'sunrise' : 'sunset'" class="h-4 w-4" :class="l.log_type === 'IN' ? 'text-green-600' : 'text-gray-500'" />
              <span class="font-medium text-gray-900">{{ l.log_type === 'IN' ? 'Started' : 'Ended' }}</span>
              <span class="text-gray-500">{{ fmtTime(l.time) }}</span>
              <div class="flex-1" />
              <a v-if="l.latitude && l.longitude" :href="mapUrl(l.latitude, l.longitude)" target="_blank" class="text-xs text-blue-600 hover:underline">Location</a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { show_alert } from '@/frappe'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'

const focusOptions = ['Visits', 'Order Collection', 'Payment Collection', 'New Outlets', 'Merchandising', 'Market Survey']

const todayState = ref({ status: 'not_started', logs: [], priorities: null, focus: null, streak: 0 })
const busy = ref(false)
const geoNote = ref('')
const priorityInputs = ref(['', '', ''])
const selectedFocus = ref([])
const placeholders = ['Most important thing today…', 'Second priority', 'Third priority']

const status = computed(() => todayState.value.status || 'not_started')
const streak = computed(() => todayState.value.streak || 0)
const priorityList = computed(() => (todayState.value.priorities || '').split('\n').map(s => s.trim()).filter(Boolean))
const focusList = computed(() => (todayState.value.focus || '').split(',').map(s => s.trim()).filter(Boolean))

const fullName = (window.frappe_boot && window.frappe_boot.full_name) || ''
const firstName = fullName.split(' ')[0] || ''
const hour = new Date().getHours()
const greeting = hour < 12 ? 'Good morning' : (hour < 17 ? 'Good afternoon' : 'Good evening')
const subGreeting = computed(() => ({
  not_started: 'Let’s set up the day.',
  checked_in: 'You’re out in the field — go get it.',
  checked_out: 'See you tomorrow.',
}[status.value] || ''))
const todayLabel = new Date().toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'short' })

function toggleFocus(opt) {
  const i = selectedFocus.value.indexOf(opt)
  if (i === -1) selectedFocus.value.push(opt)
  else selectedFocus.value.splice(i, 1)
}

function fmtTime(t) {
  if (!t) return ''
  return new Date(String(t).replace(' ', 'T')).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}
function mapUrl(lat, lng) { return `https://www.google.com/maps?q=${lat},${lng}` }

async function load() {
  try {
    todayState.value = (await call('sfa_core.api.attendance.get_attendance_today')).message
  } catch (e) {
    show_alert({ message: e.message || 'Could not load attendance', indicator: 'red' })
  }
}

function getPosition() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) return resolve(null)
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve(pos.coords),
      () => resolve(null),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    )
  })
}

async function mark(logType) {
  busy.value = true
  geoNote.value = ''
  try {
    const coords = await getPosition()
    if (!coords) geoNote.value = 'Location unavailable — recorded without GPS.'
    const isStart = logType === 'IN'
    const res = (await call('sfa_core.api.attendance.mark_attendance', {
      log_type: logType,
      latitude: coords?.latitude ?? null,
      longitude: coords?.longitude ?? null,
      accuracy: coords?.accuracy ?? null,
      priorities: isStart ? priorityInputs.value.map(s => s.trim()).filter(Boolean).join('\n') : null,
      focus: isStart ? selectedFocus.value.join(', ') : null,
    })).message
    show_alert({ message: res.log_type === 'IN' ? 'Day started — have a great one!' : 'Day ended — well done!', indicator: 'green' })
    priorityInputs.value = ['', '', '']
    selectedFocus.value = []
    await load()
  } catch (e) {
    show_alert({ message: e.message || 'Could not update attendance', indicator: 'red' })
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>
