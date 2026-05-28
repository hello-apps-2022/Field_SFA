<template>
  <SlidePanel
    :model-value="modelValue"
    @update:model-value="onClose"
    :title="headerTitle"
    :save-label="footerSaveLabel"
    :cancel-label="footerCancelLabel"
    :saving="saving"
    @save="onFooterSave"
    @cancel="onFooterCancel"
    width="560px"
  >
    <!-- Loading state -->
    <div v-if="loading" class="flex h-40 items-center justify-center">
      <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
    </div>

    <!-- VIEW MODE ───────────────────────────────────────────────── -->
    <div v-else-if="mode === 'view' && leave" class="space-y-4">
      <!-- "Awaiting your review" banner — shown when opened from an approval queue
           and the viewer can actually act on this row -->
      <div v-if="context === 'queue' && canAct" class="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 flex items-center gap-2">
        <FeatherIcon name="check-square" class="h-4 w-4 text-amber-700 shrink-0" />
        <p class="text-xs text-amber-800">
          <span class="font-medium">Awaiting your review</span>
          <span class="text-amber-600"> — approve to advance or reject with a reason.</span>
        </p>
      </div>

      <!-- Status + employee -->
      <div class="flex items-center justify-between">
        <div>
          <p class="text-xs text-gray-400">{{ leave.name }}</p>
          <p class="text-sm font-medium text-gray-900">{{ leave.employee_name || leave.employee }}</p>
        </div>
        <StatusBadge :status="leave.workflow_state" :color-map="statusColors" />
      </div>

      <!-- Rejection reason (prominent if present) -->
      <div v-if="leave.custom_rejection_reason" class="rounded-md border border-red-200 bg-red-50 px-3 py-2">
        <p class="text-[10px] font-semibold uppercase tracking-wide text-red-600">Rejection Reason</p>
        <p class="mt-1 text-sm text-red-700">{{ leave.custom_rejection_reason }}</p>
      </div>

      <!-- Core leave details grid -->
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Leave Type</p>
          <p class="font-medium text-gray-900">{{ leave.leave_type }}</p>
        </div>
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Days</p>
          <p class="font-medium text-gray-900">
            {{ leave.total_leave_days ?? '—' }}
            <span v-if="leave.half_day" class="text-xs text-gray-500">(half day)</span>
          </p>
        </div>
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">From</p>
          <p class="font-medium text-gray-900">{{ formatDate(leave.from_date) }}</p>
        </div>
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">To</p>
          <p class="font-medium text-gray-900">{{ formatDate(leave.to_date) }}</p>
        </div>
      </div>

      <!-- Reason / description -->
      <div v-if="leave.description">
        <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Reason</p>
        <p class="mt-1 text-sm text-gray-700 whitespace-pre-wrap">{{ leave.description }}</p>
      </div>

      <!-- Action buttons row ─────────────────────────────────────── -->
      <div v-if="canSubmit || canEdit || canAct" class="flex flex-wrap gap-2 border-t border-gray-100 pt-4">
        <!-- Owner controls (Draft / Rejected) -->
        <button v-if="canEdit" @click="mode = 'edit'" class="inline-flex items-center gap-1.5 rounded-md border border-gray-200 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50">
          <FeatherIcon name="edit-2" class="h-3.5 w-3.5" /> Edit
        </button>
        <button v-if="canSubmit" @click="mode = 'review'" class="inline-flex items-center gap-1.5 rounded-md bg-gray-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-gray-700">
          <FeatherIcon name="check" class="h-3.5 w-3.5" /> Submit for Approval
        </button>

        <!-- Approver controls (Pending Approval, manager/admin) -->
        <template v-if="canAct">
          <button @click="onApprove" :disabled="acting" class="inline-flex items-center gap-1.5 rounded-md bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-500 disabled:opacity-50">
            <FeatherIcon name="check" class="h-3.5 w-3.5" />
            Approve
          </button>
          <button @click="showRejectForm = true" :disabled="acting" class="inline-flex items-center gap-1.5 rounded-md border border-red-200 bg-white px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 disabled:opacity-50">
            <FeatherIcon name="x" class="h-3.5 w-3.5" />
            Reject
          </button>
        </template>
      </div>

      <!-- Reject sub-flow — textarea + confirm/cancel inline -->
      <div v-if="showRejectForm" class="rounded-md border border-red-200 bg-red-50 p-3 space-y-2">
        <label class="block text-xs font-semibold text-red-700">Reason for rejection</label>
        <textarea
          v-model="rejectReason"
          rows="3"
          placeholder="Tell the requester what to fix or why this can't be approved…"
          class="w-full rounded-md border border-red-200 bg-white px-3 py-2 text-sm focus:border-red-400 focus:outline-none"
        />
        <p v-if="rejectError" class="text-xs text-red-600">{{ rejectError }}</p>
        <div class="flex justify-end gap-2">
          <button @click="cancelReject" class="h-7 rounded-md px-3 text-xs text-gray-600 hover:bg-white">Cancel</button>
          <button @click="onReject" :disabled="acting" class="h-7 rounded-md bg-red-600 px-3 text-xs font-medium text-white hover:bg-red-500 disabled:opacity-50">
            {{ acting ? 'Rejecting…' : 'Confirm Reject' }}
          </button>
        </div>
      </div>
    </div>

    <!-- EDIT MODE ───────────────────────────────────────────────── -->
    <div v-else-if="mode === 'edit'" class="space-y-4">
      <p v-if="!isNew" class="text-xs text-gray-500">
        Editing <span class="font-medium text-gray-700">{{ leave?.name }}</span>
        — fields you change will be saved as a new Draft.
      </p>

      <!-- Leave balance hint, computed for the selected type -->
      <div v-if="selectedBalance !== null" class="rounded-md border border-blue-100 bg-blue-50 px-3 py-2 text-xs text-blue-700">
        Available balance for <span class="font-medium">{{ form.leave_type }}</span>:
        <span class="font-semibold">{{ selectedBalance }}</span> day{{ selectedBalance === 1 ? '' : 's' }}
      </div>

      <!-- Non-blocking warning if requested range exceeds available balance.
           hrms server-side decides whether to allow (depends on leave-type
           config); this hint just gives the user advance notice. -->
      <div v-if="exceedsBalance" class="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
        You're requesting <span class="font-semibold">{{ rangeDayCount }}</span> day{{ rangeDayCount === 1 ? '' : 's' }} but only
        <span class="font-semibold">{{ selectedBalance }}</span> available — this may be rejected.
      </div>

      <div>
        <label class="mb-1 block text-xs font-medium text-gray-500">Leave Type</label>
        <select v-model="form.leave_type" class="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
          <option value="" disabled>Select…</option>
          <option v-for="t in leaveTypes" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>

      <div class="flex gap-3">
        <div class="flex-1">
          <label class="mb-1 block text-xs font-medium text-gray-500">From</label>
          <input
            type="date"
            v-model="form.from_date"
            class="h-8 w-full rounded-md border px-2 text-sm focus:outline-none"
            :class="dateRangeInvalid ? 'border-red-300 focus:border-red-400' : 'border-gray-200 focus:border-gray-400'"
          />
        </div>
        <div class="flex-1">
          <label class="mb-1 block text-xs font-medium text-gray-500">To</label>
          <input
            type="date"
            v-model="form.to_date"
            :min="form.from_date || undefined"
            class="h-8 w-full rounded-md border px-2 text-sm focus:outline-none"
            :class="dateRangeInvalid ? 'border-red-300 focus:border-red-400' : 'border-gray-200 focus:border-gray-400'"
          />
        </div>
      </div>

      <!-- Live date validation hint, fires as user types (doesn't wait for Save) -->
      <p v-if="dateRangeInvalid" class="text-xs text-red-600">
        To date must be on or after From date.
      </p>

      <!-- Day-count preview when range is valid -->
      <p v-else-if="form.from_date && form.to_date && !form.half_day" class="text-xs text-gray-500">
        {{ rangeDayCount }} day{{ rangeDayCount === 1 ? '' : 's' }} requested
      </p>

      <!-- Half day is only valid when From == To. Hide the toggle otherwise. -->
      <div v-if="halfDayApplicable" class="flex items-center gap-2 text-sm">
        <input id="half-day-toggle" type="checkbox" v-model="form.half_day" class="h-4 w-4 rounded border-gray-300" />
        <label for="half-day-toggle" class="text-gray-600">Half day</label>
      </div>

      <div>
        <label class="mb-1 block text-xs font-medium text-gray-500">Reason</label>
        <textarea v-model="form.reason" rows="3" placeholder="Optional context for your approver…" class="w-full rounded-md border border-gray-200 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none"></textarea>
      </div>

      <p v-if="editError" class="text-xs text-red-600">{{ editError }}</p>
    </div>

    <!-- REVIEW MODE (pre-submit confirmation) ───────────────────── -->
    <div v-else-if="mode === 'review' && leave" class="space-y-4">
      <div class="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 flex items-start gap-2">
        <FeatherIcon name="check-square" class="h-4 w-4 text-amber-700 shrink-0 mt-0.5" />
        <p class="text-xs text-amber-800">
          <span class="font-medium">Ready to submit?</span>
          Once submitted you can't edit until it's reviewed.
        </p>
      </div>

      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Leave Type</p>
          <p class="font-medium text-gray-900">{{ leave.leave_type }}</p>
        </div>
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Days</p>
          <p class="font-medium text-gray-900">
            {{ leave.total_leave_days ?? '—' }}
            <span v-if="leave.half_day" class="text-xs text-gray-500">(half day)</span>
          </p>
        </div>
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">From</p>
          <p class="font-medium text-gray-900">{{ formatDate(leave.from_date) }}</p>
        </div>
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">To</p>
          <p class="font-medium text-gray-900">{{ formatDate(leave.to_date) }}</p>
        </div>
      </div>
      <div v-if="leave.description">
        <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Reason</p>
        <p class="mt-1 text-sm text-gray-700 whitespace-pre-wrap">{{ leave.description }}</p>
      </div>
    </div>
  </SlidePanel>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { call } from '@/utils/frappe'
import { auth } from '@/utils/auth'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: Boolean,
  // Existing leave name to load; null/empty means we're creating a new one
  leaveName: { type: String, default: '' },
  // Mode the parent wants us to OPEN in. We may transition internally afterwards.
  // 'view' for existing leaves; 'edit' for new leaves (leaveName=='')
  initialMode: { type: String, default: 'view' },
  // Caller context — 'queue' shows an "awaiting action" banner for approvers,
  // 'list' (default) shows the plain detail view. Used by LeaveApprovals.vue.
  context: { type: String, default: 'list' },
})
const emit = defineEmits(['update:modelValue', 'changed'])

const loading = ref(false)
const saving = ref(false)
const acting = ref(false)
const mode = ref('view')           // view | edit | review
const leave = ref(null)
const leaveTypes = ref([])
const balances = ref([])           // [{leave_type, balance}]
const editError = ref('')
const showRejectForm = ref(false)
const rejectReason = ref('')
const rejectError = ref('')

const isNew = computed(() => !props.leaveName)

const form = reactive({
  leave_type: '',
  from_date: '',
  to_date: '',
  half_day: false,
  reason: '',
})

const statusColors = {
  'Draft': 'bg-gray-100 text-gray-600',
  'Pending Approval': 'bg-yellow-50 text-yellow-700',
  'Approved': 'bg-green-50 text-green-700',
  'Rejected': 'bg-red-50 text-red-600',
}

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

// ── Role/state helpers ───────────────────────────────────────────
const isOwn = computed(() => leave.value && auth.employee && leave.value.employee === auth.employee)

const canEdit = computed(() =>
  leave.value && isOwn.value && ['Draft', 'Rejected'].includes(leave.value.workflow_state)
)
const canSubmit = computed(() =>
  leave.value && isOwn.value && leave.value.workflow_state === 'Draft'
)
const canAct = computed(() => {
  if (!leave.value || isOwn.value) return false
  // Single-tier: any manager or admin can act on a Pending Approval leave
  return leave.value.workflow_state === 'Pending Approval' &&
         (auth.isAdmin || auth.isManager)
})

// Half day only valid when from_date == to_date — clear the flag if user makes
// the range multi-day, otherwise hrms ignores half_day on ranges anyway.
const halfDayApplicable = computed(() =>
  form.from_date && form.to_date && form.from_date === form.to_date
)
watch(halfDayApplicable, (ok) => {
  if (!ok && form.half_day) form.half_day = false
})

// Balance for the currently selected type in the form. null = unknown / no data.
const selectedBalance = computed(() => {
  if (!form.leave_type) return null
  const hit = balances.value.find(b => b.leave_type === form.leave_type)
  return hit && hit.balance !== null && hit.balance !== undefined ? hit.balance : null
})

// Live validation: To-date inverted relative to From-date. Both ISO date strings
// (yyyy-mm-dd), so lexical compare matches chronological order. Only fires once
// BOTH dates are filled — an empty field isn't an "error", just incomplete.
const dateRangeInvalid = computed(() =>
  !!(form.from_date && form.to_date && form.to_date < form.from_date)
)

// Day count preview, inclusive of both endpoints. Calendar days only — this is
// just a hint for the user; hrms computes the authoritative total_leave_days
// server-side once submitted, factoring in the holiday list.
const rangeDayCount = computed(() => {
  if (!form.from_date || !form.to_date || dateRangeInvalid.value) return 0
  const f = dayjs(form.from_date)
  const t = dayjs(form.to_date)
  return t.diff(f, 'day') + 1
})

// Warning hint when the range exceeds the rep's current balance. Non-blocking —
// hrms decides server-side whether over-allocation is allowed. We just give
// the user advance notice so they're not surprised by a server rejection.
const exceedsBalance = computed(() =>
  selectedBalance.value !== null &&
  rangeDayCount.value > 0 &&
  rangeDayCount.value > selectedBalance.value
)

// ── Drawer header / footer derived from current mode ─────────────
const headerTitle = computed(() => {
  if (mode.value === 'edit') return isNew.value ? 'Apply for Leave' : 'Edit Leave Request'
  if (mode.value === 'review') return 'Confirm Submission'
  return 'Leave Request'
})
const footerSaveLabel = computed(() => {
  if (mode.value === 'edit') return saving.value ? 'Saving…' : 'Save Draft'
  if (mode.value === 'review') return saving.value ? 'Submitting…' : 'Submit for Approval'
  return ''        // view mode hides the footer save button (we use inline action buttons)
})
const footerCancelLabel = computed(() => {
  if (mode.value === 'edit')   return 'Cancel'
  if (mode.value === 'review') return 'Back to Edit'
  return 'Close'
})

// ── Lifecycle: open/close + data loading ─────────────────────────
watch(() => props.modelValue, (open) => {
  if (open) {
    open_()
  } else {
    reset_()
  }
})

async function open_() {
  mode.value = props.initialMode
  showRejectForm.value = false
  rejectReason.value = ''
  rejectError.value = ''
  editError.value = ''

  // Always pull meta (leave types + balance) when opening — cheap, keeps the
  // edit form responsive without an explicit refresh button.
  await loadMeta()

  if (isNew.value) {
    // Fresh form for a new application
    Object.assign(form, {
      leave_type: '',
      from_date: '',
      to_date: '',
      half_day: false,
      reason: '',
    })
    leave.value = null
    mode.value = 'edit'
  } else {
    await loadLeave()
  }
}

function reset_() {
  leave.value = null
  showRejectForm.value = false
  rejectReason.value = ''
  rejectError.value = ''
  editError.value = ''
}

async function loadMeta() {
  try {
    const [metaRes, balRes] = await Promise.all([
      call('sfa_core.api.leave.get_leave_meta'),
      // Balance is only meaningful for the current rep — admins/managers
      // viewing someone else's request don't need it. The API returns []
      // when there's no linked employee.
      auth.employee
        ? call('sfa_core.api.leave.get_leave_balance')
        : Promise.resolve({ message: { balances: [] } }),
    ])
    leaveTypes.value = metaRes.message.leave_types || []
    balances.value = balRes.message.balances || []
  } catch (e) {
    // Meta failure shouldn't block the drawer entirely — just leaves the
    // dropdown empty and balance hint absent.
    console.warn('Leave meta load failed:', e)
  }
}

async function loadLeave() {
  loading.value = true
  try {
    const res = await call('sfa_core.api.leave.get_leave_application', { name: props.leaveName })
    leave.value = res.message
    // Pre-populate the edit form from the loaded doc so "Edit" doesn't lose state
    if (leave.value) {
      Object.assign(form, {
        leave_type: leave.value.leave_type || '',
        from_date: leave.value.from_date ? dayjs(leave.value.from_date).format('YYYY-MM-DD') : '',
        to_date: leave.value.to_date ? dayjs(leave.value.to_date).format('YYYY-MM-DD') : '',
        half_day: !!leave.value.half_day,
        reason: leave.value.description || '',
      })
    }
  } finally {
    loading.value = false
  }
}

// ── Footer actions (SlidePanel emits save/cancel) ────────────────
function onFooterSave() {
  if (mode.value === 'edit')   return saveDraft()
  if (mode.value === 'review') return submitForApproval()
}
function onFooterCancel() {
  if (mode.value === 'edit') {
    // For new applications, cancelling closes the drawer entirely.
    // For edits on an existing record, cancel goes back to the view.
    if (isNew.value) onClose(false)
    else mode.value = 'view'
    return
  }
  if (mode.value === 'review') {
    mode.value = 'edit'
    return
  }
  onClose(false)
}

function onClose(v) {
  emit('update:modelValue', v)
}

// ── Validation + save/submit/approve/reject ──────────────────────
function validateForm() {
  editError.value = ''
  if (!form.leave_type) {
    editError.value = 'Pick a leave type.'
    return false
  }
  if (!form.from_date || !form.to_date) {
    editError.value = 'Both From and To dates are required.'
    return false
  }
  // Compare as ISO strings (yyyy-mm-dd) — lexical compare matches chronological order.
  if (form.to_date < form.from_date) {
    editError.value = 'To date must be on or after From date.'
    return false
  }
  if (form.half_day && form.from_date !== form.to_date) {
    // Defensive — the toggle is hidden in this case, but a stale state
    // (e.g. user changed dates after ticking half-day) could leak through.
    editError.value = 'Half day only applies to single-day requests.'
    return false
  }
  return true
}

async function saveDraft() {
  if (!validateForm()) return
  saving.value = true
  try {
    const payload = {
      leave_type: form.leave_type,
      from_date: form.from_date,
      to_date: form.to_date,
      half_day: form.half_day ? 1 : 0,
      reason: form.reason || '',
    }
    // payload is JSON-stringified because Frappe's whitelist endpoints
    // receive form-encoded args, not nested JSON objects. The backend
    // has `if isinstance(payload, str): payload = json.loads(payload)`.
    let result
    if (isNew.value) {
      result = await call('sfa_core.api.leave.apply_leave', { payload: JSON.stringify(payload) })
    } else {
      result = await call('sfa_core.api.leave.update_leave_draft', {
        name: leave.value.name, payload: JSON.stringify(payload),
      })
    }
    // Reload so view-mode has up-to-date computed fields (total_leave_days etc.)
    const nm = result.message?.name
    if (nm) {
      const r = await call('sfa_core.api.leave.get_leave_application', { name: nm })
      leave.value = r.message
    }
    mode.value = 'view'
    emit('changed')
  } catch (e) {
    editError.value = _msg(e)
  } finally {
    saving.value = false
  }
}

async function submitForApproval() {
  if (!leave.value) return
  saving.value = true
  try {
    await call('sfa_core.api.leave.submit_leave', { name: leave.value.name })
    const r = await call('sfa_core.api.leave.get_leave_application', { name: leave.value.name })
    leave.value = r.message
    mode.value = 'view'
    emit('changed')
  } catch (e) {
    // If submit fails (e.g. balance gone), bounce back to edit with the message
    editError.value = _msg(e)
    mode.value = 'edit'
  } finally {
    saving.value = false
  }
}

async function onApprove() {
  if (!leave.value) return
  const action = 'approve'
  acting.value = true
  try {
    await call('sfa_core.api.leave.action_leave', { name: leave.value.name, action })
    emit('changed')
    onClose(false)
  } catch (e) {
    alert(_msg(e))
  } finally {
    acting.value = false
  }
}

async function onReject() {
  if (!leave.value) return
  const reason = (rejectReason.value || '').trim()
  if (!reason) {
    rejectError.value = 'Reason is required.'
    return
  }
  const action = 'reject'
  acting.value = true
  rejectError.value = ''
  try {
    await call('sfa_core.api.leave.action_leave', {
      name: leave.value.name, action, reason,
    })
    emit('changed')
    onClose(false)
  } catch (e) {
    rejectError.value = _msg(e)
  } finally {
    acting.value = false
  }
}

function cancelReject() {
  showRejectForm.value = false
  rejectReason.value = ''
  rejectError.value = ''
}

// Pull a usable message out of Frappe's error envelope. Handles both
// the structured _server_messages array and a plain string fallback.
function _msg(e) {
  if (!e) return 'Something went wrong.'
  try {
    const sm = e._server_messages
    if (sm) {
      const parsed = typeof sm === 'string' ? JSON.parse(sm) : sm
      const first = Array.isArray(parsed) ? parsed[0] : parsed
      const obj = typeof first === 'string' ? JSON.parse(first) : first
      return obj.message || String(e.message || e)
    }
  } catch (_) {/* fall through */}
  return e.message || String(e)
}
</script>
