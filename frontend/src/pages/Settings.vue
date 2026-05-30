<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <router-link to="/settings" class="flex items-center justify-center h-7 w-7 rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-colors">
        <FeatherIcon name="chevron-left" class="h-4 w-4" />
      </router-link>
      <h1 class="text-sm font-semibold text-gray-900">Team</h1>
      <div class="flex-1" />
      <Btn icon="plus" variant="solid" size="sm" @click="openCreate">Add User</Btn>
    </div>

    <!-- Tabs -->
    <div class="flex shrink-0 border-b border-gray-100 bg-white px-5 gap-1">
      <button v-for="t in ['Hierarchy', 'List']" :key="t"
        class="border-b-2 px-3 py-2.5 text-sm font-medium transition-colors"
        :class="tab === t
          ? 'border-gray-900 text-gray-900'
          : 'border-transparent text-gray-500 hover:text-gray-700'"
        @click="tab = t"
      >{{ t }}</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-1 items-center justify-center">
      <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
    </div>

    <!-- Hierarchy view -->
    <div v-else-if="tab === 'Hierarchy'" class="flex-1 overflow-y-auto bg-gray-50 p-6">
      <div v-if="hierarchy.length" class="max-w-3xl mx-auto">
        <TreeNode
          v-for="node in hierarchy" :key="node.sales_person"
          :node="node"
          :is-last="true"
          :is-root="true"
          @edit="openEdit"
          @reset-password="openResetPassword"
        />
      </div>
      <div v-else class="flex flex-col items-center py-20 text-gray-400">
        <FeatherIcon name="users" class="h-10 w-10 mb-3" />
        <p class="text-sm font-medium text-gray-600">No team members yet</p>
        <Btn icon="plus" variant="solid" size="sm" class="mt-4" @click="openCreate">Add First User</Btn>
      </div>
    </div>

    <!-- List view -->
    <div v-else class="flex-1 overflow-y-auto bg-gray-50 p-5">
      <div class="space-y-2">
        <div class="grid grid-cols-12 gap-4 px-4 pb-1 text-[10px] font-semibold uppercase tracking-wide text-gray-400">
          <div class="col-span-3">Name</div>
          <div class="col-span-2">Role</div>
          <div class="col-span-2">Territory</div>
          <div class="col-span-2">Reports To</div>
          <div class="col-span-1">Last Seen</div>
          <div class="col-span-1 text-center">Status</div>
          <div class="col-span-1" />
        </div>

        <div v-for="user in users" :key="user.sales_person"
          class="grid grid-cols-12 gap-4 items-center rounded-xl border border-gray-200 bg-white px-4 py-3 hover:shadow-sm transition-shadow"
        >
          <div class="col-span-3 flex items-center gap-3 min-w-0">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-semibold"
              :class="roleColor(user.role).bg">
              <span :class="roleColor(user.role).text">{{ initials(user.full_name) }}</span>
            </div>
            <div class="min-w-0">
              <button class="text-left text-sm font-semibold text-gray-900 truncate hover:text-blue-600 hover:underline" @click="openProfile(user)">{{ user.full_name }}</button>
              <p class="text-xs text-gray-400 truncate">{{ user.email }}</p>
            </div>
          </div>
          <div class="col-span-2">
            <span class="rounded-full px-2.5 py-1 text-xs font-medium" :class="roleColor(user.role).badge">
              {{ user.role || 'No role' }}
            </span>
          </div>
          <div class="col-span-2 text-sm text-gray-600">{{ user.territory || '—' }}</div>
          <div class="col-span-2 text-sm text-gray-500">{{ user.reports_to_name || '—' }}</div>
          <div class="col-span-1 text-xs text-gray-400">{{ user.last_seen ? fmtDate(user.last_seen) : 'Never' }}</div>
          <div class="col-span-1 flex justify-center">
            <button
              class="relative inline-flex h-5 w-9 shrink-0 rounded-full border-2 border-transparent transition-colors"
              :class="user.sfa_active ? 'bg-gray-900' : 'bg-gray-200'"
              @click="toggleActive(user)"
            >
              <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                :class="user.sfa_active ? 'translate-x-4' : 'translate-x-0'" />
            </button>
          </div>
          <div class="col-span-1 flex justify-end gap-1">
            <button class="h-7 w-7 flex items-center justify-center rounded text-gray-400 hover:bg-gray-100 hover:text-blue-600"
              @click="openProfile(user)" title="View profile">
              <FeatherIcon name="user" class="h-3.5 w-3.5" />
            </button>
            <button class="h-7 w-7 flex items-center justify-center rounded text-gray-400 hover:bg-gray-100 hover:text-gray-700"
              @click="openEdit(user)">
              <FeatherIcon name="edit-2" class="h-3.5 w-3.5" />
            </button>
            <button class="h-7 w-7 flex items-center justify-center rounded text-gray-400 hover:bg-gray-100 hover:text-amber-600"
              @click="openResetPassword(user)">
              <FeatherIcon name="key" class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        <div v-if="!users.length" class="flex flex-col items-center py-16 text-gray-400">
          <FeatherIcon name="users" class="h-10 w-10 mb-3" />
          <p class="text-sm font-medium text-gray-600">No users yet</p>
          <Btn icon="plus" variant="solid" size="sm" class="mt-4" @click="openCreate">Add User</Btn>
        </div>
      </div>
    </div>
  </div>

  <!-- Create panel -->
  <SlidePanel v-model="createPanel" title="Add User" :saving="saving" save-label="Create User" @save="createUser">
    <div class="space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <FormField v-model="form.first_name" label="First Name" required :error="errors.first_name" />
        <FormField v-model="form.last_name" label="Last Name" />
      </div>
      <FormField v-model="form.email" label="Email" type="email" required :error="errors.email"
        placeholder="rep@hema.ug" />
      <FormField v-model="form.mobile_no" label="Mobile Number" placeholder="+256 7XX XXX XXX" />
      <FormField v-model="form.password" label="Password" type="password" required :error="errors.password"
        placeholder="Min 8 characters" />

      <!-- Role -->
      <div>
        <label class="mb-2 block text-xs font-medium text-gray-600">Role <span class="text-red-500">*</span></label>
        <div class="grid grid-cols-3 gap-2">
          <button v-for="r in roleOptions" :key="r.value"
            class="rounded-lg border py-2.5 px-3 text-left transition-colors"
            :class="form.role === r.value
              ? 'border-gray-900 bg-gray-900 text-white'
              : 'border-gray-200 bg-white text-gray-700 hover:border-gray-400'"
            @click="form.role = r.value"
          >
            <p class="text-xs font-semibold">{{ r.label }}</p>
            <p class="text-[10px] mt-0.5 opacity-70">{{ r.desc }}</p>
          </button>
        </div>
      </div>

      <!-- Reports To -->
      <div>
        <label class="mb-1.5 block text-xs font-medium text-gray-600">Reports To</label>
        <select v-model="form.reports_to" @change="onReportsToChange"
          class="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none">
          <option value="">— Top level (no manager) —</option>
          <option v-for="u in managerOptions" :key="u.sales_person" :value="u.sales_person">
            {{ u.full_name }} ({{ u.role }})
          </option>
        </select>
        <p class="mt-1 text-xs text-gray-400">Territory will be inherited from manager if not set</p>
      </div>

      <!-- Territory -->
      <div>
        <label class="mb-1.5 block text-xs font-medium text-gray-600">Territory</label>
        <select v-model="form.territory"
          class="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none">
          <option value="">{{ form.reports_to ? 'Inherited from manager' : 'Select territory…' }}</option>
          <option v-for="t in territories" :key="t.name" :value="t.name">{{ t.name }}</option>
        </select>
      </div>
    </div>
  </SlidePanel>

  <!-- Edit panel -->
  <SlidePanel v-model="editPanel" :title="'Edit — ' + (editUser?.full_name || '')"
    :saving="saving" save-label="Save Changes" @save="saveEdit">
    <div v-if="editUser">
      <div class="flex items-center gap-3 rounded-xl border border-gray-200 bg-gray-50 px-4 py-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold"
          :class="roleColor(editUser.role).bg">
          <span :class="roleColor(editUser.role).text">{{ initials(editUser.full_name) }}</span>
        </div>
        <div>
          <p class="text-sm font-semibold text-gray-900">{{ editUser.full_name }}</p>
          <p class="text-xs text-gray-400">{{ editUser.email }}</p>
        </div>
      </div>

      <div class="my-4 flex items-center gap-1 border-b border-gray-100">
        <button v-for="t in editTabs" :key="t" @click="editTab = t"
          class="-mb-px border-b-2 px-3 py-2 text-xs font-medium transition-colors"
          :class="editTab === t ? 'border-gray-900 text-gray-900' : 'border-transparent text-gray-400 hover:text-gray-700'">
          {{ t }}
        </button>
      </div>

      <div v-show="editTab === 'Details'" class="space-y-4">
        <div class="grid grid-cols-2 gap-3">
          <FormField v-model="editForm.first_name" label="First Name" />
          <FormField v-model="editForm.last_name" label="Last Name" />
        </div>
        <div>
          <label class="mb-2 block text-xs font-medium text-gray-600">Role</label>
          <div class="grid grid-cols-3 gap-2">
            <button v-for="r in roleOptions" :key="r.value"
              class="rounded-lg border py-2.5 px-3 text-left transition-colors"
              :class="editForm.role === r.value
                ? 'border-gray-900 bg-gray-900 text-white'
                : 'border-gray-200 bg-white text-gray-700 hover:border-gray-400'"
              @click="editForm.role = r.value">
              <p class="text-xs font-semibold">{{ r.label }}</p>
              <p class="text-[10px] mt-0.5 opacity-70">{{ r.desc }}</p>
            </button>
          </div>
        </div>
        <div>
          <label class="mb-1.5 block text-xs font-medium text-gray-600">Reports To</label>
          <select v-model="editForm.reports_to"
            class="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none">
            <option value="">— Top level —</option>
            <option v-for="u in managerOptions.filter(u => u.sales_person !== editUser.sales_person)"
              :key="u.sales_person" :value="u.sales_person">
              {{ u.full_name }} ({{ u.role }})
            </option>
          </select>
        </div>
        <div>
          <label class="mb-1.5 block text-xs font-medium text-gray-600">Territory</label>
          <select v-model="editForm.territory"
            class="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm focus:border-gray-400 focus:outline-none">
            <option value="">Select territory…</option>
            <option v-for="t in territories" :key="t.name" :value="t.name">{{ t.name }}</option>
          </select>
        </div>
        <FormField v-model="editForm.mobile_no" label="Mobile Number" />
      </div>

      <div v-show="editTab === 'Companies'" class="space-y-2">
        <p class="text-xs text-gray-400">Products this rep can sell. Leave all unchecked to allow every company. Managers and admins always see everything.</p>
        <label v-for="c in companyList" :key="c.name"
          class="flex items-center gap-2.5 rounded-lg border border-gray-200 px-3 py-2.5 text-sm text-gray-800 cursor-pointer hover:bg-gray-50">
          <input type="checkbox" :value="c.company_name" v-model="editForm.companies" class="rounded border-gray-300" />
          {{ c.company_name }}
        </label>
        <div v-if="!companyList.length" class="rounded-lg border border-dashed border-gray-200 py-4 text-center text-xs text-gray-400">
          No companies defined yet — add them under Catalog.
        </div>
      </div>

      <div v-show="editTab === 'Access'" class="space-y-4">
        <div class="flex items-center justify-between rounded-xl border border-gray-200 bg-gray-50 px-4 py-3">
          <div>
            <p class="text-sm font-medium text-gray-700">Can export reports</p>
            <p class="text-xs text-gray-400">Allow this user to download report data (Excel/CSV). Admins can always export.</p>
          </div>
          <button type="button"
            class="relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors"
            :class="editForm.can_export_reports ? 'bg-gray-900' : 'bg-gray-200'"
            @click="editForm.can_export_reports = !editForm.can_export_reports">
            <span class="inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform"
              :class="editForm.can_export_reports ? 'translate-x-4' : 'translate-x-0.5'" />
          </button>
        </div>
      </div>
    </div>
  </SlidePanel>

  <!-- Reset password -->
  <SlidePanel v-model="resetPanel" :title="'Reset Password — ' + (resetUser?.full_name || '')"
    :saving="saving" save-label="Reset Password" @save="doResetPassword">
    <div class="space-y-4">
      <div class="rounded-lg border border-amber-100 bg-amber-50 px-3 py-2.5 text-xs text-amber-700">
        The user will be able to log in with this new password immediately.
      </div>
      <FormField v-model="newPassword" label="New Password" type="password"
        required :error="errors.password" placeholder="Min 8 characters" />
    </div>
  </SlidePanel>
</template>

<!-- TreeNode: recursive interactive hierarchy component -->
<script>
import { defineComponent, ref, h } from 'vue'
import FeatherIcon from '@/components/ui/FeatherIcon.vue'

const roleStyles = {
  'SFA Admin':   { avatar: 'bg-purple-100 text-purple-700', badge: 'bg-purple-100 text-purple-700', border: 'border-purple-200' },
  'SFA Manager': { avatar: 'bg-blue-100 text-blue-700',     badge: 'bg-blue-100 text-blue-700',     border: 'border-blue-200' },
  'SFA Rep':     { avatar: 'bg-green-100 text-green-700',   badge: 'bg-green-100 text-green-700',   border: 'border-green-200' },
  'SFA Supervisor':   { avatar: 'bg-amber-100 text-amber-700', badge: 'bg-amber-100 text-amber-700', border: 'border-amber-200' },
  'SFA Field Helper': { avatar: 'bg-gray-100 text-gray-700',   badge: 'bg-gray-100 text-gray-700',   border: 'border-gray-200' },
}
const defaultStyle = { avatar: 'bg-gray-100 text-gray-600', badge: 'bg-gray-100 text-gray-600', border: 'border-gray-200' }

export const TreeNode = defineComponent({
  name: 'TreeNode',
  props: {
    node: Object,
    isLast: Boolean,
    isRoot: Boolean,
  },
  emits: ['edit', 'reset-password'],
  setup(props, { emit }) {
    const expanded = ref(true)
    const initials = (name) => (name||'?').split(' ').map(w=>w[0]).join('').toUpperCase().slice(0,2)

    return () => {
      const n = props.node
      const style = roleStyles[n.role] || defaultStyle
      const hasChildren = n.children && n.children.length > 0

      return h('div', { class: 'relative' }, [

        // Node row
        h('div', { class: 'flex items-start gap-0' }, [

          // Tree lines column (for non-root)
          !props.isRoot && h('div', { class: 'flex flex-col items-center w-8 shrink-0' }, [
            h('div', { class: 'w-px bg-gray-200 h-5 shrink-0' }),       // vertical line to parent
            h('div', { class: 'w-4 h-px bg-gray-200 mb-auto mt-0' }), // horizontal connector
          ]),

          // Card
          h('div', {
            class: `flex-1 mb-2 rounded-xl border bg-white px-4 py-3 cursor-pointer hover:shadow-sm transition-shadow ${style.border}`,
            onClick: () => emit('edit', n),
          }, [
            h('div', { class: 'flex items-center gap-3' }, [

              // Expand/collapse button (only if has children)
              hasChildren
                ? h('button', {
                    class: 'flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-gray-200 bg-gray-50 hover:bg-gray-100 transition-colors',
                    onClick: (e) => { e.stopPropagation(); expanded.value = !expanded.value },
                  }, h(FeatherIcon, {
                    name: expanded.value ? 'minus' : 'plus',
                    class: 'h-2.5 w-2.5 text-gray-500',
                  }))
                : h('div', { class: 'w-5 shrink-0' }),

              // Avatar
              h('div', { class: `flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${style.avatar}` },
                initials(n.full_name)),

              // Info
              h('div', { class: 'flex-1 min-w-0' }, [
                h('div', { class: 'flex items-center gap-2 flex-wrap' }, [
                  h('p', { class: 'text-sm font-semibold text-gray-900' }, n.full_name),
                  n.role && h('span', { class: `rounded-full px-2 py-0.5 text-[10px] font-medium ${style.badge}` }, n.role),
                  h('div', { class: `h-2 w-2 rounded-full shrink-0 ${n.sfa_active ? 'bg-green-400' : 'bg-gray-300'}` }),
                ]),
                h('p', { class: 'text-xs text-gray-400 mt-0.5' },
                  [n.territory || 'No territory', n.email ? ' · ' + n.email : '', hasChildren ? ` · ${n.children.length} direct report${n.children.length !== 1 ? 's' : ''}` : ''].filter(Boolean).join('')),
              ]),

              // Actions (stop propagation so card click doesn't trigger edit)
              h('div', { class: 'flex gap-1 shrink-0', onClick: (e) => e.stopPropagation() }, [
                h('button', {
                  class: 'h-7 w-7 flex items-center justify-center rounded text-gray-400 hover:bg-gray-100 hover:text-gray-700',
                  title: 'Edit',
                  onClick: () => emit('edit', n),
                }, h(FeatherIcon, { name: 'edit-2', class: 'h-3.5 w-3.5' })),
                h('button', {
                  class: 'h-7 w-7 flex items-center justify-center rounded text-gray-400 hover:bg-gray-100 hover:text-amber-600',
                  title: 'Reset password',
                  onClick: () => emit('reset-password', n),
                }, h(FeatherIcon, { name: 'key', class: 'h-3.5 w-3.5' })),
              ]),
            ]),
          ]),
        ]),

        // Children subtree
        hasChildren && expanded.value && h('div', { class: 'ml-8 pl-0 border-l-2 border-gray-100 ml-12' },
          n.children.map((child, i) =>
            h(TreeNode, {
              key: child.sales_person,
              node: child,
              isLast: i === n.children.length - 1,
              isRoot: false,
              onEdit: (u) => emit('edit', u),
              onResetPassword: (u) => emit('reset-password', u),
            })
          )
        ),
      ])
    }
  }
})
</script>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { call } from '@/utils/frappe'
import { useRouter } from 'vue-router'
import { successToast, errorToast } from '@/utils/toast'
import Btn from '@/components/ui/Btn.vue'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import dayjs from 'dayjs'

const tab = ref('Team')
const router = useRouter()
const users = ref([])
const hierarchy = ref([])
const loading = ref(false)
const saving = ref(false)
const createPanel = ref(false)
const editPanel = ref(false)
const resetPanel = ref(false)
const editUser = ref(null)
const resetUser = ref(null)
const newPassword = ref('')
const errors = reactive({})
const territories = ref([])

const roleOptions = [
  { value: 'SFA Rep',          label: 'Rep',        desc: 'Field sales exec' },
  { value: 'SFA Field Helper', label: 'Helper',     desc: 'Works under a rep' },
  { value: 'SFA Supervisor',   label: 'Supervisor', desc: 'Territory manager' },
  { value: 'SFA Manager',      label: 'Manager',    desc: 'All territories' },
  { value: 'SFA Admin',        label: 'Admin',      desc: 'Full access' },
]

const form = reactive({
  first_name: '', last_name: '', email: '', password: '',
  role: 'SFA Rep', territory: '', mobile_no: '', reports_to: '',
})

const editForm = reactive({
  first_name: '', last_name: '', role: '', territory: '', mobile_no: '', reports_to: '',
  can_export_reports: false, companies: [],
})

const editTabs = ['Details', 'Companies', 'Access']
const editTab = ref('Details')
const companyList = ref([])

const managerOptions = computed(() =>
  users.value.filter(u => ['SFA Admin', 'SFA Manager', 'SFA Supervisor', 'SFA Rep'].includes(u.role))
)

function roleColor(role) {
  const map = {
    'SFA Admin':   { bg: 'bg-purple-100', text: 'text-purple-700', badge: 'bg-purple-100 text-purple-700' },
    'SFA Manager': { bg: 'bg-blue-100',   text: 'text-blue-700',   badge: 'bg-blue-100 text-blue-700' },
    'SFA Rep':     { bg: 'bg-green-100',  text: 'text-green-700',  badge: 'bg-green-100 text-green-700' },
    'SFA Supervisor':   { bg: 'bg-amber-100', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-700' },
    'SFA Field Helper': { bg: 'bg-gray-100',  text: 'text-gray-600',  badge: 'bg-gray-100 text-gray-600' },
  }
  return map[role] || { bg: 'bg-gray-100', text: 'text-gray-600', badge: 'bg-gray-100 text-gray-600' }
}

function initials(name) {
  return (name||'?').split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

function onReportsToChange() {
  if (form.reports_to) {
    const manager = users.value.find(u => u.sales_person === form.reports_to)
    if (manager?.territory && !form.territory) {
      form.territory = manager.territory
    }
  }
}

async function load() {
  loading.value = true
  try {
    const [usersRes, hierRes, terrRes, coRes] = await Promise.all([
      call('sfa_core.api.settings.get_users'),
      call('sfa_core.api.settings.get_team_hierarchy'),
      call('sfa_core.api.settings.get_territories'),
      call('sfa_core.field_sfa.api.catalog.get_companies'),
    ])
    users.value = usersRes.message || []
    hierarchy.value = hierRes.message || []
    territories.value = terrRes.message || []
    companyList.value = (coRes.message || []).filter(c => c.enabled)
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function openCreate() {
  Object.assign(form, {
    first_name: '', last_name: '', email: '', password: '',
    role: 'SFA Rep', territory: '', mobile_no: '', reports_to: '',
  })
  Object.keys(errors).forEach(k => delete errors[k])
  createPanel.value = true
}

function openProfile(user) {
  router.push({ name: 'RepProfile', params: { sp: user.sales_person } })
}

function openEdit(user) {
  editUser.value = user
  const parts = (user.full_name || '').split(' ')
  Object.assign(editForm, {
    first_name: parts[0] || '',
    last_name: parts.slice(1).join(' ') || '',
    role: user.role || 'SFA Rep',
    territory: user.territory || '',
    mobile_no: user.mobile_no || '',
    reports_to: user.reports_to || '',
    can_export_reports: !!user.can_export_reports,
    companies: [...(user.companies || [])],
  })
  editTab.value = 'Details'
  editPanel.value = true
}

function openResetPassword(user) {
  resetUser.value = user
  newPassword.value = ''
  Object.keys(errors).forEach(k => delete errors[k])
  resetPanel.value = true
}

async function createUser() {
  Object.keys(errors).forEach(k => delete errors[k])
  if (!form.first_name) { errors.first_name = 'Required'; return }
  if (!form.email) { errors.email = 'Required'; return }
  if (!form.password || form.password.length < 8) { errors.password = 'Min 8 characters'; return }
  saving.value = true
  try {
    await call('sfa_core.api.settings.create_user', {
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
      password: form.password,
      role: form.role,
      territory: form.territory || null,
      mobile_no: form.mobile_no || null,
      reports_to: form.reports_to || null,
    })
    successToast(`${form.first_name} added successfully`)
    createPanel.value = false
    await load()
  } catch (e) { errorToast(e.message || 'Failed to create user') }
  finally { saving.value = false }
}

async function saveEdit() {
  if (!editUser.value) return
  saving.value = true
  try {
    await call('sfa_core.api.settings.update_user', {
      sales_person: editUser.value.sales_person,
      role: editForm.role,
      territory: editForm.territory || null,
      mobile_no: editForm.mobile_no || null,
      first_name: editForm.first_name,
      last_name: editForm.last_name,
      reports_to: editForm.reports_to || null,
      can_export_reports: editForm.can_export_reports ? 1 : 0,
      companies: JSON.stringify(editForm.companies || []),
    })
    successToast('User updated')
    editPanel.value = false
    await load()
  } catch (e) { errorToast(e.message || 'Failed') }
  finally { saving.value = false }
}

async function doResetPassword() {
  if (!newPassword.value || newPassword.value.length < 8) { errors.password = 'Min 8 characters'; return }
  saving.value = true
  try {
    await call('sfa_core.api.settings.reset_password', {
      sales_person: resetUser.value.sales_person,
      new_password: newPassword.value,
    })
    successToast('Password reset successfully')
    resetPanel.value = false
  } catch (e) { errorToast(e.message) }
  finally { saving.value = false }
}

async function toggleActive(user) {
  const newState = !user.sfa_active
  try {
    await call('sfa_core.api.settings.toggle_user_active', {
      sales_person: user.sales_person,
      enabled: newState,
    })
    user.sfa_active = newState
    successToast(newState ? `${user.full_name} activated` : `${user.full_name} deactivated`)
  } catch (e) { errorToast(e.message) }
}

const fmtDate = (d) => d ? dayjs(d).format('D MMM') : '—'

onMounted(load)
</script>
