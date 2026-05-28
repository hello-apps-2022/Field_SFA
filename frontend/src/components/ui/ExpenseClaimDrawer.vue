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
    <div v-else-if="mode === 'view' && claim" class="space-y-4">
      <!-- "Awaiting your action" banner — shown when opened from an approval queue
           and the viewer can actually act on this row -->
      <div v-if="context === 'queue' && canAct" class="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 flex items-center gap-2">
        <FeatherIcon name="check-square" class="h-4 w-4 text-amber-700 shrink-0" />
        <p class="text-xs text-amber-800">
          <span class="font-medium">Awaiting your review</span>
          <span class="text-amber-600"> — approve to advance or reject with a reason.</span>
        </p>
      </div>

      <!-- Status + name -->
      <div class="flex items-center justify-between">
        <div>
          <p class="text-xs text-gray-400">{{ claim.name }}</p>
          <p class="text-sm font-medium text-gray-900">{{ claim.employee_name || claim.employee }}</p>
        </div>
        <StatusBadge :status="claim.workflow_state" :color-map="statusColors" />
      </div>

      <!-- Rejection reason (prominent if present) -->
      <div v-if="claim.custom_rejection_reason" class="rounded-md border border-red-200 bg-red-50 px-3 py-2">
        <p class="text-[10px] font-semibold uppercase tracking-wide text-red-600">Rejection Reason</p>
        <p class="mt-1 text-sm text-red-700">{{ claim.custom_rejection_reason }}</p>
      </div>

      <!-- Activity + Purpose -->
      <div v-if="claim.custom_activity_type || claim.custom_purpose" class="space-y-1.5">
        <span v-if="claim.custom_activity_type" class="inline-flex items-center rounded-full bg-indigo-50 px-2 py-0.5 text-[10px] font-medium text-indigo-700">
          {{ claim.custom_activity_type }}
        </span>
        <p v-if="claim.custom_purpose" class="text-sm text-gray-700">{{ claim.custom_purpose }}</p>
      </div>

      <!-- Header facts -->
      <div class="grid grid-cols-2 gap-3 rounded-md border border-gray-100 bg-gray-50 p-3 text-sm">
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Date</p>
          <p class="text-gray-900">{{ formatDate(claim.posting_date) }}</p>
        </div>
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Claimed</p>
          <p class="font-medium text-gray-900">{{ fmt(claim.total_claimed_amount) }}</p>
        </div>
        <div v-if="Number(claim.total_sanctioned_amount) !== Number(claim.total_claimed_amount)">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Sanctioned</p>
          <p class="text-gray-900">{{ fmt(claim.total_sanctioned_amount) }}</p>
        </div>
      </div>

      <!-- Line items -->
      <div>
        <p class="mb-2 text-[10px] font-semibold uppercase tracking-wide text-gray-400">Expense Lines</p>
        <div class="rounded-md border border-gray-100 divide-y divide-gray-100">
          <div v-for="row in (claim.expenses || [])" :key="row.name" class="flex items-start gap-3 px-3 py-2 text-sm">
            <div class="flex-1">
              <p class="font-medium text-gray-900">{{ row.expense_type }}</p>
              <p v-if="row.description" class="text-xs text-gray-500 mt-0.5">{{ row.description }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(row.expense_date) }}</p>
            </div>
            <div class="text-right">
              <p class="font-medium text-gray-900">{{ fmt(row.amount) }}</p>
            </div>
          </div>
          <p v-if="!(claim.expenses || []).length" class="px-3 py-3 text-xs text-gray-400">No expense lines.</p>
        </div>
      </div>

      <!-- Remark -->
      <div v-if="claim.remark">
        <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Remark</p>
        <p class="mt-1 text-sm text-gray-700">{{ claim.remark }}</p>
      </div>

      <!-- Action buttons (rendered in the body, NOT the footer, since we have
           multiple action variants that don't fit SlidePanel's single-save model) -->
      <div class="border-t border-gray-100 pt-4 space-y-2">

        <!-- Owner actions: Draft/Rejected -> Edit -->
        <button
          v-if="canEdit"
          @click="enterEditMode"
          class="inline-flex h-9 w-full items-center justify-center gap-2 rounded-md border border-gray-200 bg-white px-3 text-sm font-medium text-gray-800 hover:bg-gray-50"
        >
          <FeatherIcon name="edit-2" class="h-4 w-4" /> Edit Claim
        </button>

        <!-- Owner action: Draft -> direct Submit -->
        <button
          v-if="canSubmit"
          @click="onSubmit"
          :disabled="acting"
          class="inline-flex h-9 w-full items-center justify-center gap-2 rounded-md bg-gray-900 px-3 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50"
        >
          <FeatherIcon v-if="acting" name="loader" class="h-4 w-4 animate-spin" />
          Submit for Approval
        </button>

        <!-- Approver actions: Approve / Reject (Reject reveals reason field) -->
        <template v-if="canAct && !showRejectForm">
          <div class="flex gap-2">
            <button
              @click="onApprove"
              :disabled="acting"
              class="inline-flex h-9 flex-1 items-center justify-center gap-2 rounded-md bg-green-600 px-3 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
            >
              <FeatherIcon v-if="acting" name="loader" class="h-4 w-4 animate-spin" />
              <FeatherIcon v-else name="check" class="h-4 w-4" />
              Approve
            </button>
            <button
              @click="showRejectForm = true"
              :disabled="acting"
              class="inline-flex h-9 flex-1 items-center justify-center gap-2 rounded-md border border-red-200 bg-white px-3 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
            >
              <FeatherIcon name="x" class="h-4 w-4" /> Reject
            </button>
          </div>
        </template>

        <!-- Reject sub-flow: textarea + confirm/cancel -->
        <template v-if="canAct && showRejectForm">
          <div class="rounded-md border border-red-200 bg-red-50 p-3">
            <label class="block text-[10px] font-semibold uppercase tracking-wide text-red-600 mb-1">Reason for rejection (required)</label>
            <textarea
              v-model="rejectReason"
              rows="3"
              placeholder="Explain so the rep can fix and resubmit…"
              class="w-full rounded-md border border-red-200 bg-white px-3 py-2 text-sm focus:border-red-400 focus:outline-none"
            ></textarea>
            <p v-if="rejectError" class="mt-1 text-xs text-red-600">{{ rejectError }}</p>
            <div class="mt-2 flex gap-2">
              <button
                @click="showRejectForm = false; rejectReason = ''; rejectError = ''"
                class="h-8 flex-1 rounded-md border border-gray-200 bg-white px-3 text-xs text-gray-600 hover:bg-gray-50"
              >Cancel</button>
              <button
                @click="onReject"
                :disabled="acting"
                class="inline-flex h-8 flex-1 items-center justify-center gap-1.5 rounded-md bg-red-600 px-3 text-xs font-medium text-white hover:bg-red-700 disabled:opacity-50"
              >
                <FeatherIcon v-if="acting" name="loader" class="h-3.5 w-3.5 animate-spin" />
                Confirm Reject
              </button>
            </div>
          </div>
        </template>

      </div>
    </div>

    <!-- EDIT MODE ───────────────────────────────────────────────── -->
    <div v-else-if="mode === 'edit'" class="space-y-3">
      <!-- Activity grouping -->
      <div class="space-y-2">
        <div>
          <label class="mb-1 block text-xs font-medium text-gray-500">Activity Type</label>
          <select v-model="draft.activity_type" class="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
            <option value="">Select…</option>
            <option v-for="t in activityTypes" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
        <div>
          <label class="mb-1 block text-xs font-medium text-gray-500">Purpose</label>
          <input
            v-model="draft.purpose"
            placeholder="e.g. Cheetah Launch — Kayunga East"
            class="h-8 w-full rounded-md border border-gray-200 px-2 text-sm focus:border-gray-400 focus:outline-none"
          />
        </div>
      </div>

      <div class="pt-2 border-t border-gray-100">
        <p class="mb-2 text-xs font-medium text-gray-500">Expense Lines</p>
      </div>

      <div v-for="(row, i) in draft.expenses" :key="i" class="rounded-md border border-gray-100 p-2 space-y-2">
        <!-- Row 1: Date + Type + Amount + Delete -->
        <div class="flex items-center gap-2">
          <input type="date" v-model="row.expense_date" class="h-8 w-[7.5rem] shrink-0 rounded-md border border-gray-200 px-2 text-xs focus:border-gray-400 focus:outline-none" />
          <select v-model="row.expense_type" class="h-8 flex-1 min-w-0 rounded-md border border-gray-200 bg-white px-2 text-sm focus:outline-none">
            <option value="" disabled>Type…</option>
            <option v-for="t in expenseTypes" :key="t" :value="t">{{ t }}</option>
          </select>
          <input type="number" v-model.number="row.amount" placeholder="Amount" class="h-8 w-24 shrink-0 rounded-md border border-gray-200 px-2 text-sm focus:border-gray-400 focus:outline-none" />
          <button v-if="draft.expenses.length > 1" @click="draft.expenses.splice(i,1)" class="shrink-0 text-gray-300 hover:text-red-500">
            <FeatherIcon name="x" class="h-4 w-4" />
          </button>
        </div>
        <!-- Row 2: Description (full width) -->
        <input v-model="row.description" placeholder="Description" class="h-8 w-full rounded-md border border-gray-200 px-2 text-sm focus:border-gray-400 focus:outline-none" />
      </div>
      <button @click="addLine" class="text-xs font-medium text-gray-600 hover:text-gray-900">+ Add line</button>

      <textarea v-model="draft.remark" placeholder="Remark (optional)" rows="2" class="mt-2 w-full rounded-md border border-gray-200 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none"></textarea>

      <p v-if="editError" class="text-xs text-red-600">{{ editError }}</p>
    </div>

    <!-- REVIEW MODE ───────────────────────────────────────────────── -->
    <div v-else-if="mode === 'review' && claim" class="space-y-4">
      <div class="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
        Review the details below, then Submit for Approval to send this into the workflow.
      </div>
      <div v-if="claim.custom_activity_type || claim.custom_purpose" class="space-y-1.5">
        <span v-if="claim.custom_activity_type" class="inline-flex items-center rounded-full bg-indigo-50 px-2 py-0.5 text-[10px] font-medium text-indigo-700">
          {{ claim.custom_activity_type }}
        </span>
        <p v-if="claim.custom_purpose" class="text-sm text-gray-700">{{ claim.custom_purpose }}</p>
      </div>
      <div class="grid grid-cols-2 gap-3 rounded-md border border-gray-100 bg-gray-50 p-3 text-sm">
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Date</p>
          <p class="text-gray-900">{{ formatDate(claim.posting_date) }}</p>
        </div>
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Total Claimed</p>
          <p class="font-medium text-gray-900">{{ fmt(claim.total_claimed_amount) }}</p>
        </div>
      </div>
      <div>
        <p class="mb-2 text-[10px] font-semibold uppercase tracking-wide text-gray-400">Expense Lines</p>
        <div class="rounded-md border border-gray-100 divide-y divide-gray-100">
          <div v-for="row in (claim.expenses || [])" :key="row.name" class="flex items-start gap-3 px-3 py-2 text-sm">
            <div class="flex-1">
              <p class="font-medium text-gray-900">{{ row.expense_type }}</p>
              <p v-if="row.description" class="text-xs text-gray-500 mt-0.5">{{ row.description }}</p>
            </div>
            <div class="text-right">
              <p class="font-medium text-gray-900">{{ fmt(row.amount) }}</p>
            </div>
          </div>
        </div>
      </div>
      <div v-if="claim.remark">
        <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Remark</p>
        <p class="mt-1 text-sm text-gray-700">{{ claim.remark }}</p>
      </div>
    </div>
  </SlidePanel>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { auth } from '@/utils/auth'
import { formatCurrency } from '@/utils/currency'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: Boolean,
  // Existing claim name to load; null/empty means we're creating a new one
  claimName: { type: String, default: '' },
  // Mode the parent wants us to OPEN in. We may transition internally afterwards.
  // 'view' for existing claims; 'edit' for new claims (claimName=='')
  initialMode: { type: String, default: 'view' },
  // Caller context — 'queue' shows an "awaiting action" banner for approvers,
  // 'list' (default) shows the plain detail view. Used by ExpenseApprovals.vue.
  context: { type: String, default: 'list' },
})
const emit = defineEmits(['update:modelValue', 'changed'])

const loading = ref(false)
const saving = ref(false)
const acting = ref(false)
const mode = ref('view')          // view | edit | review
const claim = ref(null)
const expenseTypes = ref([])
const activityTypes = ref([])
const editError = ref('')
const showRejectForm = ref(false)
const rejectReason = ref('')
const rejectError = ref('')

const statusColors = {
  'Draft': 'bg-gray-100 text-gray-600',
  'Pending Approval': 'bg-yellow-50 text-yellow-700',
  'Approved': 'bg-green-50 text-green-700',
  'Rejected': 'bg-red-50 text-red-600',
}

const draft = reactive({
  expenses: [{ expense_date: '', expense_type: '', amount: null, description: '' }],
  remark: '',
  activity_type: '',
  purpose: '',
})

const fmt = (v) => formatCurrency(v || 0)
const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'

// ── Role/state helpers ───────────────────────────────────────────
const isOwn = computed(() => claim.value && auth.employee && claim.value.employee === auth.employee)

const canEdit = computed(() =>
  claim.value && isOwn.value && ['Draft', 'Rejected'].includes(claim.value.workflow_state)
)
const canSubmit = computed(() =>
  claim.value && isOwn.value && claim.value.workflow_state === 'Draft'
)
const canAct = computed(() => {
  if (!claim.value || isOwn.value) return false
  // Single-tier: any manager or admin can act on a Pending Approval claim
  return claim.value.workflow_state === 'Pending Approval' &&
         (auth.isAdmin || auth.isManager)
})

// ── SlidePanel footer config (mode-dependent) ────────────────────
const headerTitle = computed(() => {
  if (!claim.value && mode.value === 'edit') return 'New Expense Claim'
  if (mode.value === 'edit') return 'Edit Expense Claim'
  if (mode.value === 'review') return 'Review & Submit'
  return 'Expense Claim'
})
const footerSaveLabel = computed(() => {
  if (mode.value === 'edit') return 'Save Draft'
  if (mode.value === 'review') return 'Submit for Approval'
  return ''  // view mode -> no footer save (actions are inline in body)
})
const footerCancelLabel = computed(() => {
  if (mode.value === 'edit') return 'Cancel'
  if (mode.value === 'review') return 'Back to Edit'
  return ''
})

// ── Lifecycle: load on open / claimName change ───────────────────
async function loadMeta() {
  try {
    const res = await call('sfa_core.api.expenses.get_expense_claim_meta')
    expenseTypes.value = res.message.expense_types || []
    activityTypes.value = res.message.activity_types || []
  } catch (e) { /* meta is best-effort */ }
}

async function loadClaim() {
  if (!props.claimName) {
    claim.value = null
    return
  }
  loading.value = true
  try {
    const res = await call('sfa_core.api.expenses.get_expense_claim', { name: props.claimName })
    claim.value = res.message
  } finally {
    loading.value = false
  }
}

function seedDraftFromClaim() {
  if (claim.value) {
    draft.activity_type = claim.value.custom_activity_type || ''
    draft.purpose = claim.value.custom_purpose || ''
    draft.remark = claim.value.remark || ''
    draft.expenses = (claim.value.expenses || []).map(r => ({
      expense_date: r.expense_date,
      expense_type: r.expense_type,
      amount: r.amount,
      description: r.description || '',
    }))
    if (!draft.expenses.length) {
      draft.expenses = [{ expense_date: dayjs().format('YYYY-MM-DD'), expense_type: '', amount: null, description: '' }]
    }
  } else {
    // New claim
    draft.activity_type = ''
    draft.purpose = ''
    draft.remark = ''
    draft.expenses = [{ expense_date: dayjs().format('YYYY-MM-DD'), expense_type: '', amount: null, description: '' }]
  }
  editError.value = ''
}

watch(() => props.modelValue, async (isOpen) => {
  if (isOpen) {
    showRejectForm.value = false
    rejectReason.value = ''
    rejectError.value = ''
    mode.value = props.initialMode
    await loadMeta()
    await loadClaim()
    // If opening in edit mode (e.g. new claim or parent jumped straight to edit),
    // seed the draft from whatever we have.
    if (mode.value === 'edit') seedDraftFromClaim()
  }
})

onMounted(() => { if (props.modelValue) loadMeta() })

// ── Mode transitions ────────────────────────────────────────────
function enterEditMode() {
  seedDraftFromClaim()
  mode.value = 'edit'
}

async function saveDraft() {
  editError.value = ''
  const valid = draft.expenses.filter(e => e.expense_type && e.amount > 0)
  if (!valid.length) { editError.value = 'Add at least one line with a type and amount.'; return false }
  saving.value = true
  try {
    const payload = {
      expenses: valid,
      remark: draft.remark,
      activity_type: draft.activity_type,
      purpose: draft.purpose,
    }
    let res
    if (claim.value && claim.value.name) {
      res = await call('sfa_core.api.expenses.update_expense_claim_draft', {
        name: claim.value.name, payload: JSON.stringify(payload),
      })
    } else {
      res = await call('sfa_core.api.expenses.create_expense_claim', {
        payload: JSON.stringify(payload),
      })
    }
    // Reload the claim so review-mode reflects what's actually saved (incl. totals).
    const name = res.message?.name
    if (name) {
      const r = await call('sfa_core.api.expenses.get_expense_claim', { name })
      claim.value = r.message
    }
    emit('changed')
    return true
  } catch (e) {
    editError.value = e.message || 'Could not save claim.'
    return false
  } finally {
    saving.value = false
  }
}

async function onFooterSave() {
  if (mode.value === 'edit') {
    const ok = await saveDraft()
    if (ok) mode.value = 'review'
  } else if (mode.value === 'review') {
    await submitFromReview()
  }
}
function onFooterCancel() {
  if (mode.value === 'edit') {
    // Cancel edit: if we have an existing claim go back to view; if new claim, close.
    if (claim.value) mode.value = 'view'
    else emit('update:modelValue', false)
  } else if (mode.value === 'review') {
    mode.value = 'edit'  // Back to Edit
  }
}

// ── Action handlers ─────────────────────────────────────────────
async function submitFromReview() {
  if (!claim.value) return
  acting.value = true
  try {
    await call('sfa_core.api.expenses.submit_expense_claim', { name: claim.value.name })
    emit('changed')
    emit('update:modelValue', false)
  } catch (e) {
    editError.value = e.message || 'Could not submit claim.'
  } finally {
    acting.value = false
  }
}

async function onSubmit() {
  if (!claim.value) return
  acting.value = true
  try {
    await call('sfa_core.api.expenses.submit_expense_claim', { name: claim.value.name })
    emit('changed')
    emit('update:modelValue', false)
  } catch (e) {
    // Surface as alert since view-mode doesn't show inline errors
    alert(e.message || 'Could not submit claim.')
  } finally {
    acting.value = false
  }
}

async function onApprove() {
  if (!claim.value) return
  const action = 'approve'
  acting.value = true
  try {
    await call('sfa_core.api.expenses.action_expense_claim', { name: claim.value.name, action })
    emit('changed')
    emit('update:modelValue', false)
  } catch (e) {
    alert(e.message || 'Could not approve.')
  } finally {
    acting.value = false
  }
}

async function onReject() {
  if (!claim.value) return
  rejectError.value = ''
  if (!rejectReason.value.trim()) { rejectError.value = 'Please enter a reason.'; return }
  const action = 'reject'
  acting.value = true
  try {
    await call('sfa_core.api.expenses.action_expense_claim', {
      name: claim.value.name, action, reason: rejectReason.value.trim(),
    })
    emit('changed')
    emit('update:modelValue', false)
  } catch (e) {
    rejectError.value = e.message || 'Could not reject.'
  } finally {
    acting.value = false
  }
}

function addLine() {
  draft.expenses.push({ expense_date: dayjs().format('YYYY-MM-DD'), expense_type: '', amount: null, description: '' })
}

function onClose(v) {
  emit('update:modelValue', v)
}
</script>
