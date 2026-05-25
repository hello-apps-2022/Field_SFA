<template>
  <div class="sfa-data-table">
    <div class="sfa-toolbar">
      <div class="sfa-search">
        <svg class="sfa-search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
          <circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.5"/>
          <path d="M11.5 11.5L14.5 14.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search..."
          @input="handleSearch"
        />
      </div>
      <div class="sfa-toolbar-actions">
        <button class="sfa-btn sfa-btn--secondary sfa-btn--sm" @click="$emit('refresh')">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M1 7C1 3.686 3.686 1 7 1c2.21 0 4.21 1.07 5.42 2.79L13 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M13 2V5M13 2H10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M13 7c0 3.314-2.686 6-6 6-2.21 0-4.21-1.07-5.42-2.79L1 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M1 12V9M1 12H4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          Refresh
        </button>
        <button class="sfa-btn sfa-btn--primary sfa-btn--sm" @click="$emit('create')">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          New
        </button>
      </div>
    </div>
    <div class="sfa-table-wrapper">
      <table class="sfa-table">
        <thead>
          <tr>
            <th v-for="col in columns" :key="col.key" :style="{ width: col.width }">
              <div class="th-content" @click="col.sortable && sort(col.key)">
                {{ col.label }}
                <span v-if="col.sortable" class="sort-indicator">
                  <svg v-if="sortKey === col.key && sortOrder === 'asc'" width="10" height="10" viewBox="0 0 10 10" fill="currentColor">
                    <path d="M5 2L2 7h6L5 2z"/>
                  </svg>
                  <svg v-else-if="sortKey === col.key && sortOrder === 'desc'" width="10" height="10" viewBox="0 0 10 10" fill="currentColor">
                    <path d="M5 8L2 3h6L5 8z"/>
                  </svg>
                  <svg v-else width="10" height="10" viewBox="0 0 10 10" fill="currentColor" opacity="0.3">
                    <path d="M5 2L2 7h6L5 2z"/>
                  </svg>
                </span>
              </div>
            </th>
            <th v-if="actions" style="width: 80px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in paginatedData"
            :key="row.name"
            :class="{ 'sfa-table-row--active': selectedRow === row.name }"
            @click="selectRow(row)"
          >
            <td v-for="col in columns" :key="col.key">
              <slot :name="'cell-' + col.key" :row="row" :value="row[col.key]">
                <span v-if="col.type === 'badge'" class="sfa-badge" :class="'sfa-badge--' + getBadgeType(row[col.key])">
                  <span class="sfa-badge-dot"></span>
                  {{ row[col.key] }}
                </span>
                <span v-else-if="col.type === 'currency'">{{ formatCurrency(row[col.key]) }}</span>
                <span v-else-if="col.type === 'datetime'">{{ formatDateTime(row[col.key]) }}</span>
                <span v-else-if="col.type === 'date'">{{ formatDate(row[col.key]) }}</span>
                <span v-else>{{ row[col.key] }}</span>
              </slot>
            </td>
            <td v-if="actions">
              <div class="row-actions">
                <button class="sfa-btn sfa-btn--ghost sfa-btn--sm" @click.stop="$emit('edit', row)">
                  Edit
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="sfa-pagination" v-if="totalPages > 1">
      <button
        class="sfa-btn sfa-btn--ghost sfa-btn--sm"
        :disabled="currentPage === 1"
        @click="currentPage--"
      >
        Previous
      </button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button
        class="sfa-btn sfa-btn--ghost sfa-btn--sm"
        :disabled="currentPage === totalPages"
        @click="currentPage++"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  data: { type: Array, required: true },
  columns: { type: Array, required: true },
  actions: { type: Boolean, default: true },
  pageSize: { type: Number, default: 20 }
});

const emit = defineEmits(['refresh', 'create', 'edit', 'select']);

const searchQuery = ref('');
const sortKey = ref('');
const sortOrder = ref('asc');
const currentPage = ref(1);
const selectedRow = ref(null);

const filteredData = computed(() => {
  let data = [...props.data];
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    data = data.filter(row =>
      props.columns.some(col =>
        String(row[col.key] || '').toLowerCase().includes(q)
      )
    );
  }
  if (sortKey.value) {
    data.sort((a, b) => {
      const aVal = a[sortKey.value];
      const bVal = b[sortKey.value];
      if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1;
      return 0;
    });
  }
  return data;
});

const totalPages = computed(() => Math.ceil(filteredData.value.length / props.pageSize));
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * props.pageSize;
  return filteredData.value.slice(start, start + props.pageSize);
});

function sort(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortOrder.value = 'asc';
  }
}

function selectRow(row) {
  selectedRow.value = row.name;
  emit('select', row);
}

function handleSearch() {
  currentPage.value = 1;
}

function getBadgeType(value) {
  const v = String(value).toLowerCase();
  if (['completed', 'active', 'paid', 'approved'].includes(v)) return 'success';
  if (['pending', 'draft', 'in progress'].includes(v)) return 'warning';
  if (['cancelled', 'missed', 'overdue', 'unpaid'].includes(v)) return 'danger';
  return 'primary';
}

function formatCurrency(val) {
  if (!val) return 'UGX 0';
  return new Intl.NumberFormat('en-UG', { style: 'currency', currency: 'UGX', maximumFractionDigits: 0 }).format(val);
}

function formatDateTime(ts) {
  if (!ts) return '';
  return new Date(ts).toLocaleString('en-UG', { dateStyle: 'medium', timeStyle: 'short' });
}

function formatDate(ts) {
  if (!ts) return '';
  return new Date(ts).toLocaleDateString('en-UG', { dateStyle: 'medium' });
}

watch(() => props.data, () => {
  currentPage.value = 1;
});
</script>

<style scoped>
.sfa-data-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  overflow: hidden;
}
.sfa-table-wrapper {
  overflow-x: auto;
}
.th-content {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  user-select: none;
}
.sort-indicator {
  display: inline-flex;
}
.row-actions {
  opacity: 0;
  transition: opacity 0.15s;
}
tr:hover .row-actions {
  opacity: 1;
}
.sfa-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-top: 1px solid #f0f2f4;
}
.page-info {
  font-size: 12px;
  color: #687178;
}
</style>
