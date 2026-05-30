<template>
  <div class="flex h-full flex-col overflow-hidden">

    <!-- Top bar -->
    <div class="flex h-[52px] shrink-0 items-center border-b border-gray-100 bg-white px-5 gap-3">
      <router-link to="/customers" class="text-sm text-gray-400 hover:text-gray-700">Customers</router-link>
      <FeatherIcon name="chevron-right" class="h-3.5 w-3.5 text-gray-300" />
      <span class="text-sm font-semibold text-gray-900 truncate">{{ doc?.customer_name || name }}</span>
      <div class="flex-1" />
      <StatusBadge v-if="doc" :status="doc.disabled ? 'Inactive' : 'Active'" />
      <Btn variant="default" icon="edit-2" size="sm" @click="editPanel = true">Edit</Btn>
    </div>

    <!-- Customer header -->
    <div class="shrink-0 border-b border-gray-100 bg-white px-5 py-4">
      <div v-if="doc" class="flex items-center gap-4">
        <!-- Avatar -->
        <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-lg font-semibold text-indigo-700">
          {{ (doc.customer_name || '?').charAt(0).toUpperCase() }}
        </div>

        <!-- Name + key fields -->
        <div class="flex-1 min-w-0">
          <h2 class="text-base font-semibold text-gray-900">{{ doc.customer_name }}</h2>
          <div class="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1.5">
            <!-- Mobile first -->
            <span class="inline-flex items-center gap-1 text-xs" :class="doc.mobile_no ? 'text-gray-700' : 'text-gray-400'">
              <FeatherIcon name="phone" class="h-3 w-3 text-gray-400" />
              {{ doc.mobile_no || 'No mobile' }}
            </span>
            <!-- Primary rep -->
            <span class="inline-flex items-center gap-1 text-xs" :class="doc.custom_sfa_rep ? 'text-gray-700' : 'text-gray-400'">
              <FeatherIcon name="user" class="h-3 w-3 text-gray-400" />
              {{ doc.custom_sfa_rep || 'No rep' }}
            </span>
            <!-- Divider -->
            <span class="text-gray-200">|</span>
            <!-- Territory -->
            <span class="inline-flex items-center gap-1 text-xs text-gray-500">
              <FeatherIcon name="globe" class="h-3 w-3 text-gray-400" />
              {{ doc.territory || 'No territory' }}
            </span>
            <!-- Group -->
            <span class="inline-flex items-center gap-1 text-xs text-gray-500">
              <FeatherIcon name="layers" class="h-3 w-3 text-gray-400" />
              {{ doc.customer_group || 'No group' }}
            </span>
            <!-- Customer type badge -->
            <span v-if="doc.customer_type" class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
              {{ doc.customer_type }}
            </span>
            <!-- Location area -->
            <span v-if="doc.custom_location_area || doc.custom_location_city" class="inline-flex items-center gap-1 text-xs text-gray-500">
              <FeatherIcon name="map-pin" class="h-3 w-3 text-gray-400" />
              {{ [doc.custom_location_area, doc.custom_location_city].filter(Boolean).join(', ') }}
            </span>
          </div>
        </div>

        <!-- Quick stats -->
        <div class="hidden sm:flex gap-5 shrink-0 text-center border-l border-gray-100 pl-5">
          <div>
            <p class="text-xl font-semibold text-gray-900">{{ doc.custom_total_orders || 0 }}</p>
            <p class="text-[10px] uppercase tracking-wide text-gray-400">Orders</p>
          </div>
          <div>
            <p class="text-xl font-semibold text-gray-900">{{ fmtShort(doc.custom_total_revenue) }}</p>
            <p class="text-[10px] uppercase tracking-wide text-gray-400">Revenue</p>
          </div>
          <div>
            <p class="text-xl font-semibold" :class="(doc.custom_outstanding_payments||0)>0?'text-orange-500':'text-gray-900'">
              {{ fmtShort(doc.custom_outstanding_payments) }}
            </p>
            <p class="text-[10px] uppercase tracking-wide text-gray-400">Due</p>
          </div>
          <div>
            <p class="text-sm font-semibold" :class="isOverdue(doc.custom_next_visit_due)?'text-red-500':'text-gray-900'">
              {{ doc.custom_last_visit_date ? formatDate(doc.custom_last_visit_date) : '—' }}
            </p>
            <p class="text-[10px] uppercase tracking-wide text-gray-400">Last visit</p>
          </div>
        </div>
      </div>

      <!-- Skeleton -->
      <div v-else class="flex items-center gap-3">
        <div class="h-12 w-12 rounded-full bg-gray-200 animate-pulse" />
        <div class="space-y-2">
          <div class="h-4 w-40 rounded bg-gray-200 animate-pulse" />
          <div class="h-3 w-64 rounded bg-gray-200 animate-pulse" />
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex shrink-0 border-b border-gray-100 bg-white px-5">
      <button v-for="tab in tabs" :key="tab.id"
        class="mr-1 border-b-2 px-3 py-2.5 text-sm font-medium transition-colors"
        :class="activeTab===tab.id ? 'border-gray-900 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700'"
        @click="activeTab=tab.id"
      >
        {{ tab.label }}
        <span v-if="tab.count" class="ml-1 rounded-full bg-gray-100 px-1.5 text-[10px] text-gray-500">{{ tab.count }}</span>
      </button>
    </div>

    <!-- Tab content -->
    <div class="flex-1 overflow-y-auto bg-gray-50">

      <!-- ── DETAILS ── -->
      <div v-show="activeTab==='details'" class="p-5">
        <div class="grid grid-cols-1 gap-5 lg:grid-cols-2">

          <!-- Left: field groups -->
          <div class="space-y-4">

            <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div class="border-b border-gray-100 bg-gray-50 px-4 py-2">
                <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Contact</p>
              </div>
              <template v-if="doc">
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Mobile</span>
                  <span class="flex-1 text-sm" :class="doc.mobile_no?'text-gray-800':'text-gray-400 italic'">{{ doc.mobile_no || 'Not set' }}</span>
                </div>
                <div class="flex px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Email</span>
                  <span class="flex-1 text-sm" :class="doc.email_id?'text-gray-800':'text-gray-400 italic'">{{ doc.email_id || 'Not set' }}</span>
                </div>
              </template>
            </div>

            <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div class="border-b border-gray-100 bg-gray-50 px-4 py-2">
                <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Classification</p>
              </div>
              <template v-if="doc">
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Customer Type</span>
                  <span class="flex-1 text-sm" :class="doc.customer_type?'text-gray-800':'text-gray-400 italic'">{{ doc.customer_type || 'Not set' }}</span>
                </div>
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Customer Group</span>
                  <span class="flex-1 text-sm" :class="doc.customer_group?'text-gray-800':'text-gray-400 italic'">{{ doc.customer_group || 'Not set' }}</span>
                </div>
                <div class="flex px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Territory</span>
                  <span class="flex-1 text-sm" :class="doc.territory?'text-gray-800':'text-gray-400 italic'">{{ doc.territory || 'Not set' }}</span>
                </div>
              </template>
            </div>

            <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div class="border-b border-gray-100 bg-gray-50 px-4 py-2">
                <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">SFA</p>
              </div>
              <template v-if="doc">
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Primary Rep</span>
                  <span class="flex-1 text-sm" :class="doc.custom_sfa_rep?'text-gray-800':'text-gray-400 italic'">{{ doc.custom_sfa_rep || 'Not assigned' }}</span>
                </div>
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Visit Frequency</span>
                  <span class="flex-1 text-sm" :class="doc.custom_visit_frequency?'text-gray-800':'text-gray-400 italic'">{{ doc.custom_visit_frequency ? doc.custom_visit_frequency + ' days' : 'Not set' }}</span>
                </div>
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Last Visit</span>
                  <span class="flex-1 text-sm text-gray-800">{{ formatDate(doc.custom_last_visit_date) }}</span>
                </div>
                <div class="flex border-b border-gray-50 px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Next Due</span>
                  <span class="flex-1 text-sm">
                    <span v-if="doc.custom_next_visit_due" :class="isOverdue(doc.custom_next_visit_due)?'text-red-600 font-medium':'text-gray-800'">
                      {{ formatDate(doc.custom_next_visit_due) }}
                      <span v-if="isOverdue(doc.custom_next_visit_due)" class="ml-1 rounded-full bg-red-50 px-2 py-0.5 text-xs text-red-600">Overdue</span>
                    </span>
                    <span v-else class="text-gray-400 italic">Not set</span>
                  </span>
                </div>
                <div class="flex px-4 py-2.5">
                  <span class="w-36 shrink-0 text-xs text-gray-400">Beat Plan</span>
                  <span class="flex-1 text-sm" :class="doc.custom_active_beat_plan?'text-gray-800':'text-gray-400 italic'">{{ doc.custom_active_beat_plan || 'None' }}</span>
                </div>
              </template>
            </div>

            <div v-if="doc" class="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div class="border-b border-gray-100 bg-gray-50 px-4 py-2">
                <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Notes</p>
              </div>
              <div class="px-4 py-3">
                <p v-if="doc.customer_details" class="text-sm text-gray-700 whitespace-pre-line">{{ doc.customer_details }}</p>
                <p v-else class="text-sm italic text-gray-400">No notes</p>
              </div>
            </div>
          </div>

          <!-- Right: map -->
          <div>
            <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <div class="flex items-center justify-between border-b border-gray-100 bg-gray-50 px-4 py-2">
                <p class="text-[10px] font-semibold uppercase tracking-wide text-gray-400">Location</p>
                <button class="text-xs text-blue-500 hover:text-blue-700 font-medium" @click="locationPanel=true">
                  {{ doc?.custom_latitude ? 'Update location' : '+ Set location' }}
                </button>
              </div>

              <div v-if="doc?.custom_latitude && doc?.custom_longitude">
                <div id="customer-map" style="height:256px;width:100%;z-index:0" />
                <!-- Address info from reverse geocoding -->
                <div class="border-t border-gray-100 px-4 py-3 space-y-1">
                  <div v-if="doc.custom_location_address" class="text-sm text-gray-700">{{ doc.custom_location_address }}</div>
                  <div class="flex items-center gap-3 text-xs text-gray-400">
                    <span class="font-mono">{{ doc.custom_latitude?.toFixed(6) }}, {{ doc.custom_longitude?.toFixed(6) }}</span>
                    <span v-if="doc.custom_location_accuracy">±{{ doc.custom_location_accuracy?.toFixed(0) }}m</span>
                  </div>
                </div>
              </div>

              <div v-else class="flex h-64 flex-col items-center justify-center text-gray-400">
                <FeatherIcon name="map-pin" class="h-10 w-10 mb-2" />
                <p class="text-sm font-medium text-gray-500">No GPS location set</p>
                <p class="text-xs mt-1 mb-4">Set from the mobile app or click below</p>
                <button class="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm text-gray-600 hover:bg-gray-50" @click="locationPanel=true">
                  Set location
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── VISITS ── -->
      <div v-show="activeTab==='summary'" class="space-y-4 p-5">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <p class="text-sm font-medium text-gray-700">Activity summary</p>
          <DateRangeFilter v-model:from="sFrom" v-model:to="sTo" @change="fetchSummary" />
        </div>

        <div v-if="summaryLoading" class="py-10 text-center text-sm text-gray-400">Loading summary…</div>

        <template v-else-if="summaryData">
          <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <div class="rounded-xl border border-gray-200 bg-white p-3">
              <p class="text-[11px] uppercase tracking-wide text-gray-400">Cartons purchased</p>
              <p class="mt-1 text-xl font-semibold text-gray-900">{{ summaryData.totals.paid_qty || 0 }}</p>
            </div>
            <div class="rounded-xl border border-gray-200 bg-white p-3">
              <p class="text-[11px] uppercase tracking-wide text-gray-400">Free cartons</p>
              <p class="mt-1 text-xl font-semibold text-green-600">{{ summaryData.totals.free_qty || 0 }}</p>
            </div>
            <div class="rounded-xl border border-gray-200 bg-white p-3">
              <p class="text-[11px] uppercase tracking-wide text-gray-400">Order value</p>
              <p class="mt-1 text-xl font-semibold text-gray-900">{{ formatUGX(summaryData.totals.value) }}</p>
            </div>
            <div class="rounded-xl border border-gray-200 bg-white p-3">
              <p class="text-[11px] uppercase tracking-wide text-gray-400">Visits</p>
              <p class="mt-1 text-xl font-semibold text-gray-900">{{ summaryData.visits.total || 0 }}</p>
            </div>
            <div class="rounded-xl border border-gray-200 bg-white p-3">
              <p class="text-[11px] uppercase tracking-wide text-gray-400">Forms filled</p>
              <p class="mt-1 text-xl font-semibold text-gray-900">{{ summaryData.forms.total || 0 }}</p>
            </div>
            <div class="rounded-xl border border-gray-200 bg-white p-3">
              <p class="text-[11px] uppercase tracking-wide text-gray-400">Cash collected</p>
              <p class="mt-1 text-xl font-semibold text-gray-900">{{ formatUGX(summaryData.payments.cash_total) }}</p>
            </div>
          </div>

          <div class="rounded-xl border border-gray-200 bg-white">
            <p class="border-b border-gray-100 px-4 py-2.5 text-sm font-medium text-gray-700">Products purchased</p>
            <div v-if="summaryData.products.length" class="divide-y divide-gray-50">
              <div class="flex items-center gap-2 px-4 py-1.5 text-[10px] font-medium uppercase tracking-wide text-gray-400">
                <span class="flex-1">Item</span><span class="w-16 text-right">Bought</span><span class="w-16 text-right">Free</span><span class="w-24 text-right">Value</span>
              </div>
              <div v-for="p in summaryData.products" :key="p.item_code" class="flex items-center gap-2 px-4 py-2 text-sm">
                <span class="flex-1 truncate text-gray-800">{{ p.item_name || p.item_code }}</span>
                <span class="w-16 text-right text-gray-900">{{ p.paid_qty || 0 }}</span>
                <span class="w-16 text-right text-green-600">{{ p.free_qty ? '+' + p.free_qty : '—' }}</span>
                <span class="w-24 text-right text-gray-700">{{ formatUGX(p.amount) }}</span>
              </div>
            </div>
            <p v-else class="px-4 py-4 text-center text-xs text-gray-400">No purchases in this range</p>
          </div>

          <div class="grid gap-3 sm:grid-cols-2">
            <div class="rounded-xl border border-gray-200 bg-white">
              <p class="border-b border-gray-100 px-4 py-2.5 text-sm font-medium text-gray-700">Visits by rep</p>
              <div v-if="summaryData.visits.by_rep.length" class="divide-y divide-gray-50">
                <div v-for="r in summaryData.visits.by_rep" :key="r.sales_person || '_'" class="flex items-center justify-between px-4 py-2 text-sm">
                  <span class="flex items-center gap-1.5 text-gray-800"><FeatherIcon name="user" class="h-3.5 w-3.5 text-gray-400" />{{ r.sales_person || 'Unassigned' }}</span>
                  <span class="font-medium text-gray-900">{{ r.cnt }}</span>
                </div>
              </div>
              <p v-else class="px-4 py-4 text-center text-xs text-gray-400">No visits in this range</p>
            </div>

            <div class="rounded-xl border border-gray-200 bg-white">
              <p class="border-b border-gray-100 px-4 py-2.5 text-sm font-medium text-gray-700">Payments</p>
              <div class="divide-y divide-gray-50">
                <div v-for="r in summaryData.payments.by_type" :key="r.payment_type || '_'" class="flex items-center justify-between px-4 py-2 text-sm">
                  <span class="text-gray-700">{{ r.payment_type || 'Cash' }} <span class="text-gray-400">×{{ r.cnt }}</span></span>
                  <span class="font-medium text-gray-900">{{ formatUGX(r.amt) }}</span>
                </div>
                <div v-if="summaryData.payments.carton_count" class="flex items-center justify-between px-4 py-2 text-sm">
                  <span class="text-gray-700">Cartons <span class="text-gray-400">×{{ summaryData.payments.carton_count }}</span></span>
                  <span class="font-medium text-gray-900">{{ summaryData.payments.carton_total != null ? summaryData.payments.carton_total + ' ctns' : '—' }}</span>
                </div>
                <p v-if="!summaryData.payments.by_type.length && !summaryData.payments.carton_count" class="px-4 py-4 text-center text-xs text-gray-400">No payments in this range</p>
              </div>
            </div>
          </div>
        </template>
      </div>

      <div v-show="activeTab==='visits'" class="p-5">
        <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
          <p class="text-sm text-gray-500">{{ fVisits.length }} visits</p>
          <div class="flex items-center gap-2">
            <DateRangeFilter v-model:from="vFrom" v-model:to="vTo" />
            <Btn variant="solid" icon="plus" size="sm" @click="newVisitPanel=true">New Visit</Btn>
          </div>
        </div>
        <div v-if="fVisits.length" class="space-y-2">
          <div v-for="v in fVisits" :key="v.name"
            class="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4 cursor-pointer hover:bg-gray-50"
            @click="$router.push('/visits/'+v.name)"
          >
            <div class="flex items-center gap-3">
              <div class="h-2 w-2 rounded-full shrink-0"
                :class="{'bg-green-500':v.status==='In Progress','bg-blue-400':v.status==='Completed','bg-gray-300':v.status==='Open','bg-red-400':v.status==='Cancelled'}" />
              <div>
                <p class="text-sm font-medium text-gray-900">{{ formatDate(v.visit_date) }}<span v-if="v.check_in_time" class="ml-1.5 text-xs font-normal text-gray-400">{{ formatTime(v.check_in_time) }}</span></p>
                <p class="text-xs text-gray-500">{{ v.sales_person }}{{ v.visit_purpose?' · '+v.visit_purpose:'' }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span v-if="v.duration_minutes" class="text-xs text-gray-400">{{ v.duration_minutes }}min</span>
              <StatusBadge :status="v.status" />
              <FeatherIcon name="chevron-right" class="h-4 w-4 text-gray-300" />
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center py-16 text-gray-400">
          <FeatherIcon name="map-pin" class="h-10 w-10 mb-3" />
          <p class="text-sm font-medium text-gray-600">No visits yet</p>
        </div>
      </div>

      <!-- ── FORMS ── -->
      <div v-show="activeTab==='forms'" class="p-5">
        <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
          <p class="text-sm text-gray-500">{{ fForms.length }} responses</p>
          <div class="flex items-center gap-2">
            <DateRangeFilter v-model:from="fFrom" v-model:to="fTo" />
            <Btn variant="solid" icon="file-text" size="sm" @click="fillFormPanel=true">Fill Form</Btn>
          </div>
        </div>
        <div v-if="fForms.length" class="space-y-2">
          <div v-for="r in fForms" :key="r.name"
          class="rounded-xl border border-gray-200 bg-white p-4 cursor-pointer hover:bg-gray-50 transition-colors"
          @click="selectedResponseName = r.name; responsePanel = true"
        >
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-start gap-3">
                <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-50">
                  <FeatherIcon name="file-text" class="h-4 w-4 text-blue-500" />
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ r.form_template }}</p>
                  <div class="mt-1 flex flex-wrap items-center gap-x-3 gap-y-0.5 text-xs text-gray-400">
                    <span v-if="r.sales_person || r.owner" class="flex items-center gap-1">
                      <FeatherIcon name="user" class="h-3 w-3" />{{ r.sales_person || r.owner }}
                    </span>
                    <span class="flex items-center gap-1">
                      <FeatherIcon name="calendar" class="h-3 w-3" />{{ formatDate(r.response_date) }}
                      <span class="text-gray-300 ml-1">{{ formatTime(r.response_date) }}</span>
                    </span>
                    <router-link v-if="r.visit" :to="'/visits/'+r.visit"
                      class="flex items-center gap-1 text-blue-400 hover:text-blue-600 hover:underline"
                      @click.stop>
                      <FeatherIcon name="map-pin" class="h-3 w-3" />{{ r.visit }}
                    </router-link>
                  </div>
                </div>
              </div>
              <StatusBadge :status="r.sync_status" />
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center py-10 text-gray-400">
          <FeatherIcon name="file-text" class="h-10 w-10 mb-3" />
          <p class="text-sm font-medium text-gray-600">No forms submitted yet</p>
          <p class="text-xs mt-1 mb-4">Use the button above to fill a form for this customer</p>
          <Btn variant="default" icon="file-text" size="sm" @click="fillFormPanel=true">Fill Form</Btn>
        </div>
      </div>

      <!-- ── ORDERS ── -->
      <div v-show="activeTab==='orders'" class="p-5">
        <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
          <p class="text-sm text-gray-500">{{ fOrders.length }} orders · {{ formatUGX(fOrders.reduce((s,o)=>s+(o.grand_total||0),0)) }} total</p>
          <div class="flex items-center gap-2">
            <DateRangeFilter v-model:from="oFrom" v-model:to="oTo" />
            <Btn variant="solid" icon="plus" size="sm" @click="openNewOrder">New Order</Btn>
          </div>
        </div>
        <div class="mb-3 flex flex-wrap gap-1.5">
          <button v-for="s in ['','Draft','Confirmed','Delivered','Cancelled']" :key="s" type="button" @click="orderStatusFilter=s"
            class="rounded-full px-2.5 py-1 text-xs font-medium transition-colors"
            :class="orderStatusFilter===s ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
            {{ s || 'All' }}
          </button>
        </div>
        <div v-if="fOrders.length" class="space-y-2">
          <div v-for="o in fOrders" :key="o.name"
            class="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4 cursor-pointer hover:bg-gray-50"
            @click="openOrder(o)"
          >
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <p class="text-sm font-mono font-medium text-gray-900">{{ o.name }}</p>
                <span class="inline-flex items-center gap-1 rounded bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-500">
                  <FeatherIcon :name="o.custom_sfa_order_type === 'Van Sale' ? 'truck' : 'clipboard'" class="h-3 w-3" />
                  {{ o.custom_sfa_order_type || 'Booking' }}
                </span>
              </div>
              <div class="mt-1 flex flex-wrap items-center gap-x-2.5 gap-y-0.5 text-xs text-gray-500">
                <span class="flex items-center gap-1"><FeatherIcon name="calendar" class="h-3 w-3 text-gray-400" />{{ formatDate(o.transaction_date) }}</span>
                <span>{{ o.total_qty || 0 }} ctns</span>
                <span v-if="o.custom_sfa_rep || o.owner" class="flex items-center gap-1"><FeatherIcon name="user" class="h-3 w-3 text-gray-400" />{{ o.custom_sfa_rep || o.owner }}</span>
                <span v-if="o.custom_sfa_delivered_on" class="flex items-center gap-1 text-green-600"><FeatherIcon name="check-circle" class="h-3 w-3" />Delivered {{ formatDate(o.custom_sfa_delivered_on) }}</span>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div class="text-right">
                <p class="text-sm font-semibold text-gray-900">{{ formatUGX(o.grand_total) }}</p>
                <span class="rounded px-1.5 py-0.5 text-[10px] font-medium" :class="orderStateColor(orderState(o))">{{ orderState(o) }}</span>
              </div>
              <FeatherIcon name="chevron-right" class="h-4 w-4 text-gray-300" />
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center py-16 text-gray-400">
          <FeatherIcon name="shopping-cart" class="h-10 w-10 mb-3" />
          <p class="text-sm font-medium text-gray-600">No orders yet</p>
        </div>
      </div>

      <!-- ── PAYMENTS ── -->
      <div v-show="activeTab==='payments'" class="p-5">
        <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
          <p class="text-sm text-gray-500">{{ fPayments.length }} payments</p>
          <div class="flex items-center gap-2">
            <DateRangeFilter v-model:from="pFrom" v-model:to="pTo" />
            <Btn variant="solid" icon="plus" size="sm" @click="newPaymentPanel=true">Record Payment</Btn>
          </div>
        </div>
        <div v-if="fPayments.length" class="space-y-2">
          <div v-for="p in fPayments" :key="p.name"
            class="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4">
            <div>
              <p class="text-sm font-semibold text-gray-900">{{ formatUGX(p.amount) }}</p>
              <p class="text-xs text-gray-500">{{ p.payment_type }} · {{ formatDate(p.payment_date) }}</p>
              <p v-if="p.sales_person" class="flex items-center gap-1 text-xs text-gray-400"><FeatherIcon name="user" class="h-3 w-3" />{{ p.sales_person }}</p>
              <p v-if="p.reference_no" class="text-xs text-gray-400">Ref: {{ p.reference_no }}</p>
            </div>
            <StatusBadge :status="p.status" />
          </div>
        </div>
        <div v-else class="flex flex-col items-center py-16 text-gray-400">
          <FeatherIcon name="credit-card" class="h-10 w-10 mb-3" />
          <p class="text-sm font-medium text-gray-600">No payments yet</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Edit Panel -->
  <SlidePanel v-model="editPanel" title="Edit Customer" :saving="saving" @save="save">
    <div class="space-y-4">
      <FormField v-model="form.customer_name" label="Customer Name" required />
      <FormField v-model="form.customer_type" label="Customer Type" type="select" :options="['Company','Individual']" />
      <FormField v-model="form.customer_group" label="Customer Group" type="select" :options="customerGroups" />
      <FormField v-model="form.territory" label="Territory" type="select" :options="territories" />
      <FormField v-model="form.mobile_no" label="Mobile" type="tel" />
      <FormField v-model="form.email_id" label="Email" type="email" />
      <FormField v-model="form.custom_sfa_rep" label="Primary Sales Rep" type="select" :options="salesPersons" />
      <FormField v-model="form.custom_visit_frequency" label="Visit Frequency (days)" type="number" />
      <FormField v-model="form.customer_details" label="Notes" type="textarea" />
    </div>
  </SlidePanel>

  <!-- Location Panel -->
  <SlidePanel v-model="locationPanel" title="Set Customer Location" :saving="savingLocation" save-label="Save Location" @save="saveLocation" width="520px">
    <div class="space-y-4">
      <p class="text-sm text-gray-600">Click anywhere on the map to place a pin. The address will be auto-filled from the coordinates.</p>
      <div id="location-picker-map" class="h-72 w-full rounded-xl border border-gray-200 overflow-hidden" />
      <div class="grid grid-cols-2 gap-3">
        <FormField v-model="locationForm.latitude" label="Latitude" type="number" />
        <FormField v-model="locationForm.longitude" label="Longitude" type="number" />
      </div>
      <div v-if="geocoding" class="flex items-center gap-2 text-xs text-gray-400">
        <FeatherIcon name="loader" class="h-3.5 w-3.5 animate-spin" />
        Looking up address...
      </div>
      <div v-if="locationForm.address" class="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2.5">
        <p class="text-xs font-medium text-gray-500 mb-0.5">Address found</p>
        <p class="text-sm text-gray-800">{{ locationForm.address }}</p>
      </div>
    </div>
  </SlidePanel>

  <!-- New Visit Panel -->
  <SlidePanel v-model="newVisitPanel" title="New Visit" :saving="savingVisit" save-label="Create Visit" @save="createVisit">
    <div class="space-y-4">
      <div class="rounded-lg bg-gray-50 border border-gray-200 px-3 py-2.5 text-sm text-gray-700">
        <span class="text-xs text-gray-400 block mb-0.5">Customer</span>
        {{ doc?.customer_name }}
      </div>
      <FormField v-model="visitForm.sales_person" label="Sales Person" type="select" :options="salesPersons" required :error="visitErrors.sales_person" />
      <FormField v-model="visitForm.beat_plan" label="Beat Plan" type="select" :options="beatPlans" />
      <FormField v-model="visitForm.visit_date" label="Visit Date" type="date" required />
      <FormField v-model="visitForm.visit_purpose" label="Purpose" type="select"
        :options="['Sales Order','Payment Collection','Stock Check','Merchandising','Relationship','Other']" />
      <FormField v-model="visitForm.status" label="Status" type="select"
        :options="['Open','In Progress','Completed']" />
      <FormField v-model="visitForm.notes" label="Notes" type="textarea" />
    </div>
  </SlidePanel>

  <!-- New Order Panel -->
  <SlidePanel v-model="newOrderPanel" :title="editingOrder ? 'Edit Order' : (orderForm.order_type === 'Van Sale' ? 'Van Sale' : 'New Order')" :saving="savingOrder" :save-label="orderForm.order_type === 'Van Sale' ? 'Record Sale' : 'Save Draft'" @save="saveOrder" width="560px">
    <div class="space-y-4">
      <div class="rounded-lg bg-gray-50 border border-gray-200 px-3 py-2.5 text-sm text-gray-700">
        <span class="text-xs text-gray-400 block mb-0.5">Customer</span>
        {{ doc?.customer_name }}
      </div>
      <FormField v-model="orderForm.order_type" label="Order Type" type="select" :options="[{value:'Booking',label:'Booking — deliver later'},{value:'Van Sale',label:'Van Sale — immediate'}]" />
      <FormField v-model="orderForm.transaction_date" label="Order Date" type="date" required />
      <FormField v-model="orderForm.delivery_date" label="Delivery Date" type="date" :min="orderForm.transaction_date" />
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="text-xs font-medium text-gray-600">Items <span class="text-red-500">*</span></label>
          <button class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-800" @click="addItem">
            <FeatherIcon name="plus" class="h-3 w-3" /> Add Item
          </button>
        </div>
        <div class="mb-2 space-y-2">
          <div v-if="categories.length" class="flex gap-1 overflow-x-auto pb-0.5">
            <button type="button" @click="itemCategory=''"
              class="shrink-0 rounded-full px-2.5 py-1 text-xs font-medium transition-colors"
              :class="itemCategory==='' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">All</button>
            <button v-for="c in categories" :key="c" type="button" @click="itemCategory=c"
              class="shrink-0 rounded-full px-2.5 py-1 text-xs font-medium transition-colors"
              :class="itemCategory===c ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">{{ c }}</button>
          </div>
          <input v-model="itemSearch" ref="productSearch" type="text" placeholder="Search products to add…"
            class="w-full rounded-md border border-gray-200 px-2.5 py-1.5 text-sm focus:border-gray-400 focus:outline-none" />
          <div v-if="itemSearch || itemCategory" class="max-h-44 divide-y divide-gray-50 overflow-y-auto rounded-lg border border-gray-100">
            <button v-for="it in filteredItems" :key="it.value" type="button" @click="addProduct(it)"
              class="flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-gray-50">
              <span class="truncate text-gray-800">{{ it.label }}</span>
              <FeatherIcon name="plus-circle" class="ml-2 h-4 w-4 shrink-0 text-gray-400" />
            </button>
            <div v-if="!filteredItems.length" class="px-3 py-3 text-center text-xs text-gray-400">No products match</div>
          </div>
        </div>
        <!-- Column headers -->
        <div v-if="orderForm.items.length" class="mb-1 flex items-center gap-2 px-0.5">
          <span class="flex-1 text-[10px] font-medium uppercase tracking-wide text-gray-400">Item</span>
          <span class="w-14 text-center text-[10px] font-medium uppercase tracking-wide text-gray-400">Qty</span>
          <span class="w-20 text-center text-[10px] font-medium uppercase tracking-wide text-gray-400">Rate ({{ currencyLabel() }})</span>
          <span v-if="showFreeCol" class="w-16 text-center text-[10px] font-medium uppercase tracking-wide text-gray-400">Free</span>
          <span class="w-5" />
        </div>
        <div class="space-y-2">
          <div v-for="(row, i) in orderForm.items" :key="i" class="space-y-1">
            <div class="flex items-center gap-2">
              <select v-model="row.item_code" @change="onItemChange(row)"
                class="flex-1 rounded-md border border-gray-200 bg-white px-2 py-2 text-sm focus:border-gray-400 focus:outline-none">
                <option value="">Select item...</option>
                <option v-for="it in filteredItems" :key="it.value" :value="it.value">{{ it.label }}</option>
                <option v-if="row.item_code && !inFiltered(row.item_code)" :value="row.item_code">{{ row.item_name || row.item_code }}</option>
              </select>
              <input v-model.number="row.qty" type="number" min="1" @change="applyFreeSchemes"
                class="w-14 rounded-md border border-gray-200 px-2 py-2 text-sm text-center focus:border-gray-400 focus:outline-none"
                title="Quantity" />
              <input v-model.number="row.rate" type="number" min="0" :readonly="row.is_free"
                class="w-20 rounded-md border border-gray-200 px-2 py-2 text-sm text-right focus:border-gray-400 focus:outline-none"
                :class="row.is_free ? 'bg-gray-50 text-gray-400' : ''"
                title="Unit rate" />
              <div v-if="showFreeCol" class="flex w-16 shrink-0 justify-center">
                <span v-if="row.is_free && row._scheme" class="rounded bg-green-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-green-700" title="Scheme free item">Free</span>
                <button v-else-if="auth.allowDiscretionaryFree" type="button" @click="toggleFree(row)"
                  class="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase transition-colors"
                  :class="row.is_free ? 'bg-green-100 text-green-700' : 'border border-gray-200 text-gray-400 hover:border-green-300 hover:text-green-600'"
                  :title="row.is_free ? 'Unmark free' : 'Give this line free'">
                  <FeatherIcon v-if="row.is_free" name="check" class="h-3 w-3" /> Free
                </button>
              </div>
              <button @click="removeItem(i)" class="shrink-0 text-gray-300 hover:text-red-500 transition-colors" title="Remove">
                <FeatherIcon name="x" class="h-3.5 w-3.5" />
              </button>
            </div>
            <div v-if="row.is_free" class="pr-6 text-right text-xs text-green-600">
              {{ row.qty }} × free<span v-if="row._for"> · with {{ row._for }}</span> = <span class="font-medium">{{ formatUGX(0) }}</span>
            </div>
            <div v-else-if="row.item_code && row.qty && row.rate" class="pr-6 text-right text-xs text-gray-400">
              {{ row.qty }} × {{ formatUGX(row.rate) }} = <span class="font-medium text-gray-700">{{ formatUGX(row.qty * row.rate) }}</span>
            </div>
          </div>
          <div v-if="!orderForm.items.length" class="rounded-lg border border-dashed border-gray-200 py-4 text-center text-xs text-gray-400">
            No items yet — search above and tap a product, or use “+ Add Item”
          </div>
        </div>
        <div v-if="orderTotal > 0" class="mt-2 text-right text-sm font-semibold text-gray-800">
          Total: {{ formatUGX(orderTotal) }}
        </div>
      </div>
      <FormField v-model="orderForm.remarks" label="Remarks" type="textarea" />
    </div>
  </SlidePanel>

  <!-- Order view -->
  <SlidePanel v-model="orderViewPanel" :title="viewOrderDoc ? viewOrderDoc.name : 'Order'" save-label="" width="520px">
    <div v-if="viewOrderDoc" class="space-y-4">
      <div class="flex items-center justify-between rounded-xl border border-gray-200 bg-gray-50 px-4 py-3">
        <div>
          <p class="text-xs text-gray-400">{{ formatDate(viewOrderDoc.transaction_date) }}</p>
          <p class="text-sm font-semibold text-gray-900">{{ formatUGX(viewOrderDoc.grand_total) }}</p>
        </div>
        <span class="rounded px-2 py-0.5 text-xs font-medium" :class="orderStateColor(viewState)">{{ viewState }}</span>
      </div>
      <div class="flex items-center gap-4 px-1 text-xs text-gray-500">
        <span class="flex items-center gap-1">
          <FeatherIcon :name="viewOrderDoc.custom_sfa_order_type === 'Van Sale' ? 'truck' : 'clipboard'" class="h-3.5 w-3.5" />
          {{ viewOrderDoc.custom_sfa_order_type || 'Booking' }}
        </span>
        <span v-if="viewState === 'Delivered' && viewOrderDoc.custom_sfa_delivered_on" class="text-green-600">
          Delivered {{ formatDate(viewOrderDoc.custom_sfa_delivered_on) }}
        </span>
      </div>
      <div>
        <p class="mb-2 text-xs font-medium text-gray-600">Items</p>
        <div class="divide-y divide-gray-50 rounded-lg border border-gray-100">
          <div v-for="(it, idx) in (viewOrderDoc.items || [])" :key="idx" class="flex items-center justify-between px-3 py-2.5 text-sm">
            <div class="min-w-0">
              <p class="truncate text-gray-800">
                {{ it.item_name || it.item_code }}
                <span v-if="it.is_free_item" class="ml-1 rounded bg-green-100 px-1 text-[9px] font-semibold uppercase text-green-700">Free</span>
              </p>
              <p class="text-[11px] text-gray-400">{{ it.qty }} × {{ it.is_free_item ? 'free' : formatUGX(it.rate) }}</p>
            </div>
            <span class="text-sm text-gray-700">{{ formatUGX(it.amount) }}</span>
          </div>
          <div v-if="!(viewOrderDoc.items || []).length" class="px-3 py-6 text-center text-xs text-gray-400">No items</div>
        </div>
      </div>
      <div v-if="viewOrderDoc.remarks" class="rounded-lg bg-gray-50 px-3 py-2.5 text-sm text-gray-600">
        <span class="mb-0.5 block text-xs text-gray-400">Remarks</span>{{ viewOrderDoc.remarks }}
      </div>
      <div v-if="viewState === 'Draft' || viewState === 'Confirmed'" class="flex flex-wrap gap-2 border-t border-gray-100 pt-4">
        <template v-if="viewState === 'Draft'">
          <Btn variant="solid" size="sm" icon="check" :loading="savingAction" @click="doConfirm(viewOrderDoc.name)">Confirm</Btn>
          <Btn variant="subtle" size="sm" icon="edit-2" @click="openEditDraft(viewOrderDoc)">Edit</Btn>
          <Btn variant="ghost" size="sm" icon="trash-2" @click="deleteDraft(viewOrderDoc.name)">Delete</Btn>
        </template>
        <template v-else>
          <Btn variant="solid" size="sm" icon="truck" :loading="savingAction" @click="doDeliver(viewOrderDoc.name)">Mark Delivered</Btn>
          <Btn variant="ghost" size="sm" icon="x-circle" @click="doCancel(viewOrderDoc.name)">Cancel Order</Btn>
        </template>
      </div>
    </div>
  </SlidePanel>

  <!-- New Payment Panel -->
  <SlidePanel v-model="newPaymentPanel" title="Record Payment" :saving="savingPayment" save-label="Record" @save="createPayment">
    <div class="space-y-4">
      <!-- Customer context -->
      <div class="rounded-lg bg-gray-50 border border-gray-200 px-3 py-2.5 text-sm text-gray-700">
        <span class="text-xs text-gray-400 block mb-0.5">Customer</span>
        {{ doc?.customer_name }}
      </div>

      <FormField v-model="paymentForm.sales_person" label="Sales Person" type="select" :options="salesPersons" required :error="paymentErrors.sales_person" />
      <FormField v-model="paymentForm.payment_date" label="Payment Date" type="date" required />

      <!-- Payment Mode toggle -->
      <div>
        <label class="mb-1.5 block text-xs font-medium text-gray-600">Payment Mode</label>
        <div class="flex rounded-lg border border-gray-200 overflow-hidden">
          <button
            class="flex-1 py-2 text-sm font-medium transition-colors flex items-center justify-center gap-1.5"
            :class="paymentForm.payment_mode === 'Cash' ? 'bg-gray-900 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'"
            @click="paymentForm.payment_mode = 'Cash'"
          >
            <FeatherIcon name="credit-card" class="h-3.5 w-3.5" /> Cash
          </button>
          <button
            class="flex-1 py-2 text-sm font-medium transition-colors flex items-center justify-center gap-1.5 border-l border-gray-200"
            :class="paymentForm.payment_mode === 'Cartons' ? 'bg-gray-900 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'"
            @click="paymentForm.payment_mode = 'Cartons'"
          >
            <FeatherIcon name="package" class="h-3.5 w-3.5" /> Cartons
          </button>
        </div>
        <p class="mt-1 text-[10px] text-gray-400">
          {{ paymentForm.payment_mode === 'Cartons' ? 'Record items and carton quantities — no pricing required' : 'Enter the cash amount collected' }}
        </p>
      </div>

      <!-- Cash mode -->
      <template v-if="paymentForm.payment_mode === 'Cash'">
        <FormField v-model="paymentForm.payment_type" label="Payment Type" type="select"
          :options="['Cash','Cheque','Bank Transfer','Credit Note']" required :error="paymentErrors.payment_type" />
        <FormField v-model="paymentForm.amount" :label="`Amount (${currencyLabel()})`" type="number" required :error="paymentErrors.amount" />
        <FormField v-model="paymentForm.reference_no" label="Reference / Receipt No" />
      </template>

      <!-- Carton mode -->
      <template v-else>
        <div>
          <div class="flex items-center justify-between mb-1.5">
            <label class="text-xs font-medium text-gray-600">Items <span class="text-red-500">*</span></label>
            <button class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-800" @click="addCartonItem">
              <FeatherIcon name="plus" class="h-3 w-3" /> Add Item
            </button>
          </div>

          <div v-if="paymentForm.carton_items.length" class="mb-1.5 flex items-center gap-2 px-0.5">
            <span class="flex-1 text-[10px] font-medium uppercase tracking-wide text-gray-400">Item</span>
            <span class="w-20 text-center text-[10px] font-medium uppercase tracking-wide text-gray-400">Cartons</span>
            <span class="w-5" />
          </div>

          <div class="space-y-2">
            <div v-for="(row, i) in paymentForm.carton_items" :key="i" class="flex items-center gap-2">
              <select v-model="row.item_code" @change="onCartonItemChange(row)"
                class="flex-1 rounded-md border border-gray-200 bg-white px-2 py-2 text-sm focus:border-gray-400 focus:outline-none">
                <option value="">Select item…</option>
                <option v-for="it in items" :key="it.value" :value="it.value">{{ it.label }}</option>
              </select>
              <input v-model.number="row.cartons" type="number" min="0" placeholder="0"
                class="w-20 rounded-md border border-gray-200 px-2 py-2 text-sm text-center focus:border-gray-400 focus:outline-none" />
              <button @click="removeCartonItem(i)" class="shrink-0 text-gray-300 hover:text-red-500 transition-colors">
                <FeatherIcon name="x" class="h-3.5 w-3.5" />
              </button>
            </div>
            <div v-if="!paymentForm.carton_items.length" class="rounded-lg border border-dashed border-gray-200 py-4 text-center text-xs text-gray-400">
              No items added — click "+ Add Item" above
            </div>
          </div>

          <div v-if="paymentForm.carton_items.some(r => r.item_code && r.cartons > 0)"
            class="mt-3 rounded-lg bg-amber-50 border border-amber-100 px-3 py-2">
            <p class="text-xs font-medium text-amber-700">
              {{ paymentForm.carton_items.filter(r => r.item_code && r.cartons > 0).reduce((s,r) => s + r.cartons, 0) }} total cartons
            </p>
            <p class="text-[10px] text-amber-600 mt-0.5">No monetary value — carton-based credit</p>
          </div>
        </div>
        <FormField v-model="paymentForm.reference_no" label="Reference / Delivery Note No" />
      </template>

      <FormField v-model="paymentForm.notes" label="Notes" type="textarea" />
    </div>
  </SlidePanel>
  <!-- Fill Form Panel -->
  <FillFormPanel
    v-model="fillFormPanel"
    :customer-name="doc?.customer_name"
    :customer-doc="doc"
    :recent-visits="visits"
    @submitted="load(); activeTab='forms'"
  />

  <!-- View Form Response -->
  <FormResponsePanel
    v-model="responsePanel"
    :response-name="selectedResponseName"
  />
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'

import { getDoc, getList, saveDoc, insertDoc, deleteDoc, call } from '@/utils/frappe'
import { successToast, errorToast } from '@/utils/toast'
import { useLinkedData } from '@/composables/useLinkedData'
import SlidePanel from '@/components/ui/SlidePanel.vue'
import FillFormPanel from '@/components/ui/FillFormPanel.vue'
import FormResponsePanel from '@/components/ui/FormResponsePanel.vue'
import FormField from '@/components/ui/FormField.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import Btn from '@/components/ui/Btn.vue'
import DateRangeFilter from '@/components/ui/DateRangeFilter.vue'
import { formatCurrency, formatCurrencyShort, currencyLabel } from '@/utils/currency'
import dayjs from 'dayjs'
import { getL, ensureLeafletCSS } from '@/utils/leaflet'

const props = defineProps({ name: String })
const {
  customerGroups, territories, salesPersons, beatPlans, items, paymentTypes,
  loadCustomerGroups, loadTerritories, loadSalesPersons, loadBeatPlans, loadItems, loadPaymentTypes,
} = useLinkedData()

const doc = ref(null)
const visits = ref([])
const orders = ref([])
const payments = ref([])
const formResponses = ref([])
const vFrom = ref(''), vTo = ref('')
const fFrom = ref(''), fTo = ref('')
const oFrom = ref(''), oTo = ref('')
const orderStatusFilter = ref('')
const summaryData = ref(null)
const summaryLoading = ref(false)
const sFrom = ref(''), sTo = ref('')
const pFrom = ref(''), pTo = ref('')
function inDateRange(d, from, to) {
  if (!d) return true
  const x = dayjs(d)
  if (from && x.isBefore(dayjs(from).startOf('day'))) return false
  if (to && x.isAfter(dayjs(to).endOf('day'))) return false
  return true
}
const fVisits = computed(() => visits.value.filter(v => inDateRange(v.visit_date, vFrom.value, vTo.value)))
const fForms = computed(() => formResponses.value.filter(r => inDateRange(r.response_date, fFrom.value, fTo.value)))
const fOrders = computed(() => orders.value.filter(o => inDateRange(o.transaction_date, oFrom.value, oTo.value) && (!orderStatusFilter.value || orderState(o) === orderStatusFilter.value)))
const fPayments = computed(() => payments.value.filter(p => inDateRange(p.payment_date, pFrom.value, pTo.value)))
const activeTab = ref('details')

const editPanel = ref(false)
const locationPanel = ref(false)
const newVisitPanel = ref(false)
const newOrderPanel = ref(false)
const orderViewPanel = ref(false)
const viewOrderDoc = ref(null)
async function openOrder(o) {
  try {
    viewOrderDoc.value = await getDoc('Sales Order', o.name)
    orderViewPanel.value = true
  } catch (e) { errorToast(e.message || 'Failed to load order') }
}
const editingOrder = ref(null)
const savingAction = ref(false)
function orderState(o) {
  if (o.docstatus === 2) return 'Cancelled'
  if (o.docstatus === 0) return 'Draft'
  if (o.custom_sfa_delivery_status === 'Delivered') return 'Delivered'
  return 'Confirmed'
}
function orderStateColor(s) {
  return ({ Draft:'bg-yellow-50 text-yellow-700', Confirmed:'bg-indigo-50 text-indigo-700', Delivered:'bg-green-50 text-green-700', Cancelled:'bg-red-50 text-red-600' })[s] || 'bg-gray-100 text-gray-600'
}
const viewState = computed(() => viewOrderDoc.value ? orderState(viewOrderDoc.value) : '')
function openNewOrder() {
  editingOrder.value = null
  orderForm.items = []
  orderForm.transaction_date = dayjs().format('YYYY-MM-DD')
  orderForm.delivery_date = ''
  orderForm.remarks = ''
  orderForm.order_type = 'Booking'
  newOrderPanel.value = true
}
async function openEditDraft(o) {
  try {
    const d = await getDoc('Sales Order', o.name)
    editingOrder.value = d.name
    orderForm.transaction_date = d.transaction_date
    orderForm.delivery_date = d.delivery_date || ''
    orderForm.remarks = d.remarks || ''
    orderForm.order_type = d.custom_sfa_order_type || 'Booking'
    orderForm.items = (d.items || []).map(it => ({ item_code: it.item_code, item_name: it.item_name, qty: it.qty, rate: it.is_free_item ? 0 : it.rate, is_free: !!it.is_free_item }))
    orderViewPanel.value = false
    newOrderPanel.value = true
  } catch (e) { errorToast(e.message || 'Failed to load order') }
}
async function doConfirm(name) {
  savingAction.value = true
  try { await call('sfa_core.field_sfa.api.order_actions.confirm_order', { name }); successToast('Order confirmed'); orderViewPanel.value = false; await load() }
  catch (e) { errorToast(e.message || 'Failed to confirm') } finally { savingAction.value = false }
}
async function doDeliver(name) {
  savingAction.value = true
  try { await call('sfa_core.field_sfa.api.order_actions.mark_delivered', { name }); successToast('Marked delivered'); orderViewPanel.value = false; await load() }
  catch (e) { errorToast(e.message || 'Failed') } finally { savingAction.value = false }
}
async function doCancel(name) {
  if (!confirm('Cancel this order? This cannot be undone.')) return
  savingAction.value = true
  try { await call('sfa_core.field_sfa.api.order_actions.cancel_order', { name }); successToast('Order cancelled'); orderViewPanel.value = false; await load() }
  catch (e) { errorToast(e.message || 'Failed to cancel') } finally { savingAction.value = false }
}
async function deleteDraft(name) {
  if (!confirm('Delete this draft?')) return
  savingAction.value = true
  try { await deleteDoc('Sales Order', name); successToast('Draft deleted'); orderViewPanel.value = false; await load() }
  catch (e) { errorToast(e.message || 'Failed to delete') } finally { savingAction.value = false }
}
const newPaymentPanel = ref(false)
const fillFormPanel = ref(false)
const responsePanel = ref(false)
const selectedResponseName = ref('')

const saving = ref(false)
const savingLocation = ref(false)
const savingVisit = ref(false)
const savingOrder = ref(false)
const savingPayment = ref(false)
const geocoding = ref(false)

const form = reactive({ customer_name:'', customer_type:'Company', customer_group:'', territory:'', mobile_no:'', email_id:'', customer_details:'', custom_sfa_rep:'', custom_visit_frequency:'' })
const locationForm = reactive({ latitude:'', longitude:'', area:'', city:'', district:'', address:'' })
import { auth } from '@/utils/auth'

const visitForm = reactive({ sales_person: auth.salesPerson || '', beat_plan:'', visit_date:dayjs().format('YYYY-MM-DD'), visit_purpose:'', status:'Open', notes:'' })
const visitErrors = reactive({})
const orderForm = reactive({ transaction_date:dayjs().format('YYYY-MM-DD'), delivery_date:'', items:[], remarks:'', order_type:'Booking' })

// ── Free carton schemes (auto-suggest removable rate-0 lines) ───────────────
const freeSchemes = ref([])
const dismissedSchemes = ref(new Set())

async function loadFreeSchemes() {
  try {
    const res = await call('sfa_core.field_sfa.api.free_carton.get_free_carton_schemes', { customer: props.name })
    freeSchemes.value = res.message || []
  } catch (e) { freeSchemes.value = [] }
}

function paidQtyMap() {
  const m = {}
  for (const r of orderForm.items) {
    if (r.is_free || !r.item_code) continue
    m[r.item_code] = (m[r.item_code] || 0) + (Number(r.qty) || 0)
  }
  return m
}

function applyFreeSchemes() {
  const qmap = paidQtyMap()
  // Recompute scheme-driven free rows from scratch (scaled by purchase multiples).
  const desired = []
  for (const s of freeSchemes.value) {
    if (dismissedSchemes.value.has(s.name)) continue
    const bought = qmap[s.buy_item] || 0
    if (s.buy_qty > 0 && bought >= s.buy_qty) {
      const multiples = Math.floor(bought / s.buy_qty)
      const freeQty = multiples * (s.free_qty || 0)
      if (freeQty > 0) desired.push({ scheme: s.name, free_item: s.free_item, qty: freeQty, buy_item: s.buy_item })
    }
  }
  // Keep paid rows + discretionary free rows (no _scheme); replace all scheme free rows.
  orderForm.items = orderForm.items.filter(r => !(r.is_free && r._scheme))
  for (const d of desired) {
    const it = items.value.find(i => i.value === d.free_item)
    const buyIt = items.value.find(i => i.value === d.buy_item)
    orderForm.items.push({ item_code: d.free_item, item_name: it ? it.label : d.free_item, qty: d.qty, rate: 0, is_free: true, _scheme: d.scheme, _for: buyIt ? buyIt.label : d.buy_item })
  }
}

watch(newOrderPanel, (open) => {
  if (open) { dismissedSchemes.value = new Set(); loadFreeSchemes() }
})
const paymentForm = reactive({
  sales_person: auth.salesPerson || '', payment_date: dayjs().format('YYYY-MM-DD'),
  payment_mode: 'Cash', payment_type: '', amount: '',
  reference_no: '', notes: '',
  carton_items: [],
})
const paymentErrors = reactive({})

const cartonTotal = computed(() => 0) // No pricing in carton mode

function addCartonItem() {
  paymentForm.carton_items.push({ item_code: '', item_name: '', cartons: 1, rate_per_carton: 0 })
}
function removeCartonItem(i) { paymentForm.carton_items.splice(i, 1) }
function onCartonItemChange(row) {
  const item = items.value.find(i => i.value === row.item_code)
  if (item) row.item_name = item.label
}

const orderTotal = computed(() => orderForm.items.reduce((s,i) => s+(i.qty||0)*(i.rate||0), 0))
const showFreeCol = computed(() => auth.allowDiscretionaryFree || (freeSchemes.value && freeSchemes.value.length > 0))
const allowedItems = computed(() => {
  const cos = auth.companies || []
  if (auth.isAdmin || auth.isManager || !cos.length) return items.value
  return items.value.filter(it => !it.company || cos.includes(it.company))
})
const itemCategory = ref('')
const itemSearch = ref('')
const productSearch = ref(null)
const categories = computed(() => {
  const s = new Set()
  for (const it of allowedItems.value) { if (it.category) s.add(it.category) }
  return [...s].sort()
})
const filteredItems = computed(() => {
  const q = itemSearch.value.trim().toLowerCase()
  return allowedItems.value.filter(it =>
    (!itemCategory.value || it.category === itemCategory.value) &&
    (!q || (it.label || '').toLowerCase().includes(q)))
})
function inFiltered(code) { return filteredItems.value.some(it => it.value === code) }
async function fetchSummary() {
  summaryLoading.value = true
  try {
    const r = await call('sfa_core.field_sfa.api.customer_summary.get_customer_summary', { customer: props.name, date_from: sFrom.value || null, date_to: sTo.value || null })
    summaryData.value = r && r.message ? r.message : r
  } catch (e) { errorToast(e.message || 'Failed to load summary') }
  finally { summaryLoading.value = false }
}
watch(activeTab, (v) => { if (v === 'summary' && !summaryData.value) fetchSummary() })

const tabs = computed(() => [
  { id:'details', label:'Details' },
  { id:'summary', label:'Summary' },
  { id:'visits', label:'Visits', count: visits.value.length||null },
  { id:'forms', label:'Forms', count: formResponses.value.length||null },
  { id:'orders', label:'Orders', count: orders.value.length||null },
  { id:'payments', label:'Payments', count: payments.value.length||null },
])

async function load() {
  const [d, v, fr, o, p] = await Promise.all([
    getDoc('Customer', props.name),
    getList('SFA Visit', { fields:['name','visit_date','sales_person','status','visit_purpose','duration_minutes','check_in_time'], filters:{customer:props.name}, orderBy:'visit_date desc, creation desc', limit:50 }),
    getList('SFA Form Response', { fields:['name','form_template','response_date','sync_status','sales_person','visit','owner'], filters:{customer:props.name}, orderBy:'response_date desc', limit:30 }),
    getList('Sales Order', { fields:['name','transaction_date','status','docstatus','grand_total','total_qty','custom_sfa_rep','delivery_date','custom_sfa_order_type','custom_sfa_delivery_status','custom_sfa_delivered_on','custom_sfa_delivered_by','owner'], filters:{customer:props.name}, orderBy:'transaction_date desc, creation desc', limit:50 }),
    getList('SFA Payment', { fields:['name','payment_date','payment_type','amount','status','reference_no','sales_person'], filters:{customer:props.name}, orderBy:'payment_date desc, creation desc', limit:50 }),
  ])
  doc.value = d
  visits.value = v
  formResponses.value = fr
  orders.value = o
  payments.value = p
  Object.assign(form, {
    customer_name: d.customer_name||'', customer_type: d.customer_type||'Company',
    customer_group: d.customer_group||'', territory: d.territory||'',
    mobile_no: d.mobile_no||'', email_id: d.email_id||'',
    customer_details: d.customer_details||'', custom_sfa_rep: d.custom_sfa_rep||'',
    custom_visit_frequency: d.custom_visit_frequency||'',
  })
  if (d.custom_latitude && d.custom_longitude) {
    await nextTick()
    initMap(d.custom_latitude, d.custom_longitude, d.customer_name)
  }
}

// ── Leaflet helpers ───────────────────────────────────────────────────────

function makeIcon(color='#4f46e5') {
  return L.divIcon({ className:'', iconSize:[16,16], iconAnchor:[8,8],
    html:`<div style="background:${color};width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4)"></div>` })
}

async function initMap(lat, lng, label) {
  await ensureLeafletCSS()
  const L = await getL()
  const el = document.getElementById('customer-map')
  if (!el) return
  if (el._map) {
    el._map.invalidateSize()
    el._map.setView([lat, lng], 16)
    return
  }
  const map = L.map(el)
  el._map = map
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(map)
  map.setView([lat, lng], 16)
  L.marker([lat, lng], { icon: makeIcon() }).addTo(map).bindPopup(`<b>${label}</b>`).openPopup()
  window.setTimeout(() => map.invalidateSize(), 100)
}

let pickerMap = null
let pickerMarker = null

async function openLocationPicker() {
  locationForm.latitude = doc.value?.custom_latitude || ''
  locationForm.longitude = doc.value?.custom_longitude || ''
  locationForm.address = doc.value?.custom_location_address || ''
  await nextTick()
  await ensureLeafletCSS()
  const L = await getL()
  const el = document.getElementById('location-picker-map')
  if (!el) return
  if (pickerMap) { pickerMap.remove(); pickerMap = null; pickerMarker = null }
  const center = locationForm.latitude ? [+locationForm.latitude, +locationForm.longitude] : [0.3476, 32.5825]
  pickerMap = L.map(el)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(pickerMap)
  pickerMap.setView(center, locationForm.latitude ? 16 : 12)
  window.setTimeout(() => pickerMap.invalidateSize(), 100)
  if (locationForm.latitude) {
    pickerMarker = L.marker(center, { icon: makeIcon(), draggable: true }).addTo(pickerMap)
    pickerMarker.on('dragend', (e) => setPickerCoords(e.target.getLatLng().lat, e.target.getLatLng().lng))
  }
  pickerMap.on('click', (e) => {
    setPickerCoords(e.latlng.lat, e.latlng.lng)
    if (pickerMarker) pickerMap.removeLayer(pickerMarker)
    pickerMarker = L.marker([e.latlng.lat, e.latlng.lng], { icon: makeIcon(), draggable: true }).addTo(pickerMap)
    pickerMarker.on('dragend', (ev) => setPickerCoords(ev.target.getLatLng().lat, ev.target.getLatLng().lng))
  })
}

async function setPickerCoords(lat, lng) {
  locationForm.latitude = lat.toFixed(6)
  locationForm.longitude = lng.toFixed(6)
  await reverseGeocode(lat, lng)
}

async function reverseGeocode(lat, lng) {
  geocoding.value = true
  locationForm.address = ''
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`,
      { headers: { 'Accept-Language': 'en', 'User-Agent': 'HemaSFA/1.0' } }
    )
    const data = await res.json()
    if (data.address) {
      const a = data.address
      locationForm.area = a.suburb || a.neighbourhood || a.village || a.hamlet || ''
      locationForm.city = a.city || a.town || a.municipality || a.county || ''
      locationForm.district = a.county || a.state_district || a.state || ''
      locationForm.address = data.display_name || ''
    }
  } catch (e) {
    console.error('Geocode failed', e)
  } finally {
    geocoding.value = false
  }
}

watch(locationPanel, async (val) => { if (val) await openLocationPicker() })
watch(activeTab, async (val) => {
  if (val === 'details' && doc.value?.custom_latitude) {
    await nextTick()
    initMap(doc.value.custom_latitude, doc.value.custom_longitude, doc.value.customer_name)
  }
})

// ── Save handlers ─────────────────────────────────────────────────────────
async function save() {
  saving.value = true
  try {
    await saveDoc({
      doctype:'Customer', name:props.name, customer_type:'Company',
      customer_name: form.customer_name, customer_group: form.customer_group,
      territory: form.territory, mobile_no: form.mobile_no, email_id: form.email_id,
      customer_details: form.customer_details, custom_sfa_rep: form.custom_sfa_rep,
      custom_visit_frequency: form.custom_visit_frequency,
    })
    successToast('Customer updated')
    editPanel.value = false
    await load()
  } catch (e) { errorToast(e.message || 'Save failed') }
  finally { saving.value = false }
}

async function saveLocation() {
  if (!locationForm.latitude || !locationForm.longitude) { errorToast('Click on the map to set a location'); return }
  savingLocation.value = true
  try {
    await saveDoc({
      doctype:'Customer', name:props.name, customer_type:'Company',
      custom_latitude: parseFloat(locationForm.latitude),
      custom_longitude: parseFloat(locationForm.longitude),
      custom_location_area: locationForm.area,
      custom_location_city: locationForm.city,
      custom_location_district: locationForm.district,
      custom_location_address: locationForm.address,
    })
    successToast('Location saved')
    locationPanel.value = false
    await load()
  } catch (e) { errorToast(e.message || 'Save failed') }
  finally { savingLocation.value = false }
}

async function createVisit() {
  if (!visitForm.sales_person) { visitErrors.sales_person = 'Required'; return }
  savingVisit.value = true
  try {
    await insertDoc({ doctype:'SFA Visit', customer:props.name, ...visitForm })
    successToast('Visit created')
    newVisitPanel.value = false
    await load()
  } catch (e) { errorToast(e.message || 'Failed') }
  finally { savingVisit.value = false }
}

function addItem() { orderForm.items.push({ item_code:'', qty:1, rate:0, item_name:'' }) }
function addProduct(it) {
  orderForm.items.push({ item_code: it.value, item_name: it.label, qty: 1, rate: it.rate || 0, is_free: false })
  applyFreeSchemes()
  nextTick(() => { productSearch.value?.focus() })
}
function removeItem(i) {
  const r = orderForm.items[i]
  if (r && r.is_free && r._scheme) dismissedSchemes.value.add(r._scheme)
  orderForm.items.splice(i,1)
}
function onItemChange(row) {
  // Duplicate lines are allowed: the same SKU can be both paid and free.
  const item = items.value.find(i => i.value===row.item_code)
  if (item) { row.item_name = item.label; if (!row.is_free) row.rate = item.rate||0 }
  applyFreeSchemes()
}
function toggleFree(row) {
  row.is_free = !row.is_free
  if (row.is_free) { row.rate = 0; delete row._scheme; delete row._for }
  else { const it = items.value.find(i => i.value === row.item_code); row.rate = it ? (it.rate || 0) : 0 }
  applyFreeSchemes()
}

async function saveOrder() {
  if (!orderForm.items.some(i => i.item_code)) { errorToast('Add at least one item'); return }
  savingOrder.value = true
  try {
    // Aggregate duplicate lines by item + free-flag: paid X lines merge into one,
    // free X lines merge into one, but a paid line and a free line of the same
    // SKU stay distinct.
    const _agg = {}
    for (const i of orderForm.items) {
      if (!i.item_code) continue
      const free = i.is_free ? 1 : 0
      const key = i.item_code + '|' + free
      if (!_agg[key]) _agg[key] = { item_code:i.item_code, item_name:i.item_name, qty:0, rate: free ? 0 : (Number(i.rate)||0), is_free_item: free }
      _agg[key].qty += (Number(i.qty)||0)
      if (!free && (Number(i.rate)||0)) _agg[key].rate = Number(i.rate)||0
    }
    const payloadItems = Object.values(_agg).filter(r => r.qty > 0).map(r => ({
      doctype:'Sales Order Item', item_code:r.item_code, item_name:r.item_name,
      qty:r.qty, rate:r.rate, is_free_item:r.is_free_item,
      delivery_date: orderForm.delivery_date||orderForm.transaction_date,
    }))
    let name = editingOrder.value
    if (name) {
      await saveDoc({
        doctype: 'Sales Order', name,
        transaction_date: orderForm.transaction_date,
        delivery_date: orderForm.delivery_date || orderForm.transaction_date,
        remarks: orderForm.remarks,
        custom_sfa_order_type: orderForm.order_type,
        items: payloadItems,
      })
    } else {
      const created = await insertDoc({
        doctype:'Sales Order', customer:props.name, naming_series:'SAL-ORD-.YYYY.-',
        transaction_date: orderForm.transaction_date,
        delivery_date: orderForm.delivery_date || orderForm.transaction_date,
        remarks: orderForm.remarks,
        custom_sfa_order_type: orderForm.order_type,
        ...(auth.salesPerson ? { custom_sfa_rep: auth.salesPerson } : {}),
        items: payloadItems,
      })
      name = created.name
    }
    if (orderForm.order_type === 'Van Sale') {
      await call('sfa_core.field_sfa.api.order_actions.confirm_order', { name })
      await call('sfa_core.field_sfa.api.order_actions.mark_delivered', { name })
      successToast('Sale recorded')
    } else {
      successToast(editingOrder.value ? 'Draft updated' : 'Draft saved')
    }
    const savedName = name
    const wasVanSale = orderForm.order_type === 'Van Sale'
    newOrderPanel.value = false
    editingOrder.value = null
    orderForm.items = []
    await load()
    if (!wasVanSale && savedName) {
      try { viewOrderDoc.value = await getDoc('Sales Order', savedName); orderViewPanel.value = true } catch (e) {}
    }
  } catch (e) { errorToast(e.message || 'Failed') }
  finally { savingOrder.value = false }
}

async function createPayment() {
  Object.keys(paymentErrors).forEach(k => delete paymentErrors[k])
  if (!paymentForm.sales_person) { paymentErrors.sales_person = 'Required'; return }

  if (paymentForm.payment_mode === 'Cash') {
    if (!paymentForm.payment_type) { paymentErrors.payment_type = 'Required'; return }
    if (!paymentForm.amount || Number(paymentForm.amount) <= 0) { paymentErrors.amount = 'Enter a valid amount'; return }
  } else {
    const validItems = paymentForm.carton_items.filter(r => r.item_code && r.cartons > 0 && r.rate_per_carton > 0)
    if (!validItems.length) { errorToast('Add at least one item with cartons and rate'); return }
  }

  savingPayment.value = true
  try {
    const isCarton = paymentForm.payment_mode === 'Cartons'
    const finalAmount = isCarton ? 0 : Number(paymentForm.amount)
    const cartonItems = isCarton
      ? paymentForm.carton_items.filter(r => r.item_code && r.cartons > 0).map(r => ({
          doctype: 'SFA Payment Carton Item',
          item_code: r.item_code, item_name: r.item_name,
          cartons: r.cartons,
        }))
      : []

    await insertDoc({
      doctype: 'SFA Payment', customer: props.name,
      sales_person: paymentForm.sales_person,
      payment_date: paymentForm.payment_date,
      payment_type: isCarton ? 'Cartons' : paymentForm.payment_type,
      amount: isCarton ? 0 : finalAmount,
      custom_payment_mode: paymentForm.payment_mode,
      custom_carton_total: 0,
      custom_carton_items: cartonItems,
      reference_no: paymentForm.reference_no,
      notes: paymentForm.notes, status: 'Draft',
    })

    successToast('Payment recorded')
    newPaymentPanel.value = false
    paymentForm.carton_items = []
    paymentForm.payment_mode = 'Cash'
    await load()
  } catch (e) { errorToast(e.message || 'Failed') }
  finally { savingPayment.value = false }
}

const formatDate = (d) => d ? dayjs(d).format('D MMM YYYY') : '—'
const formatTime = (d) => d ? dayjs(d).format('HH:mm') : ''
const isOverdue = (d) => d && dayjs(d).isBefore(dayjs(), 'day')
const formatUGX = formatCurrency
const fmtShort = formatCurrencyShort
const fmt = formatCurrency

const route = useRoute()

onMounted(async () => {
  await load()
  loadCustomerGroups(); loadTerritories(); loadSalesPersons()
  loadBeatPlans(); loadItems(); loadPaymentTypes()
  // Auto-open tab from query param (e.g. navigating from Orders/Payments page)
  if (route.query.tab) activeTab.value = route.query.tab
})
</script>

<style>
.leaflet-tile-container img,.leaflet-marker-pane img,.leaflet-shadow-pane img{max-width:none!important;width:auto!important;height:auto!important}
.leaflet-container{z-index:0;font-family:inherit}
</style>
