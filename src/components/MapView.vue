<template>
  <div class="sfa-map-view">
    <div class="map-toolbar">
      <div class="map-filters">
        <button
          v-for="filter in filters"
          :key="filter.value"
          class="filter-chip"
          :class="{ active: activeFilter === filter.value }"
          @click="activeFilter = filter.value"
        >
          {{ filter.label }}
        </button>
      </div>
      <div class="map-actions">
        <button class="sfa-btn sfa-btn--secondary sfa-btn--sm" @click="fitBounds">
          Fit All
        </button>
        <button class="sfa-btn sfa-btn--secondary sfa-btn--sm" @click="refresh">
          Refresh
        </button>
      </div>
    </div>
    <div class="map-container" ref="mapContainer">
      <div class="map-placeholder">
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
          <path d="M32 4L8 16v32l24 12 24-12V16L32 4z" stroke="#2490EF" stroke-width="2" fill="none"/>
          <circle cx="32" cy="28" r="8" stroke="#2490EF" stroke-width="2" fill="none"/>
          <path d="M32 36v12" stroke="#2490EF" stroke-width="2"/>
        </svg>
        <p>Map integration ready for Mapbox / OpenStreetMap</p>
        <p class="map-subtitle">{{ markers.length }} locations loaded</p>
      </div>
      <div class="map-markers-list">
        <div
          v-for="marker in filteredMarkers"
          :key="marker.id"
          class="map-marker-item"
          :class="{ active: selectedMarker === marker.id }"
          @click="selectMarker(marker)"
        >
          <div class="marker-icon" :class="'marker--' + marker.type">
            {{ marker.type === 'visit' ? 'V' : marker.type === 'customer' ? 'C' : 'R' }}
          </div>
          <div class="marker-info">
            <div class="marker-name">{{ marker.name }}</div>
            <div class="marker-coords">{{ formatCoord(marker.lat) }}, {{ formatCoord(marker.lng) }}</div>
          </div>
          <div class="marker-status" :class="marker.status">{{ marker.status }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  markers: { type: Array, default: () => [] }
});

const emit = defineEmits(['select', 'refresh']);

const activeFilter = ref('all');
const selectedMarker = ref(null);
const mapContainer = ref(null);

const filters = [
  { label: 'All', value: 'all' },
  { label: 'Visits', value: 'visit' },
  { label: 'Customers', value: 'customer' },
  { label: 'Reps', value: 'rep' }
];

const filteredMarkers = computed(() => {
  if (activeFilter.value === 'all') return props.markers;
  return props.markers.filter(m => m.type === activeFilter.value);
});

function selectMarker(marker) {
  selectedMarker.value = marker.id;
  emit('select', marker);
}

function fitBounds() {
  console.log('Fit bounds to all markers');
}

function refresh() {
  emit('refresh');
}

function formatCoord(val) {
  if (val === null || val === undefined) return 'N/A';
  return val.toFixed(4);
}
</script>

<style scoped>
.sfa-map-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}
.map-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f2f4;
}
.map-filters {
  display: flex;
  gap: 8px;
}
.filter-chip {
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid #e2e6e9;
  background: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.filter-chip:hover, .filter-chip.active {
  background: #2490EF;
  color: white;
  border-color: #2490EF;
}
.map-actions {
  display: flex;
  gap: 8px;
}
.map-container {
  flex: 1;
  display: flex;
  position: relative;
}
.map-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  color: #687178;
}
.map-placeholder p {
  margin-top: 12px;
  font-size: 14px;
}
.map-subtitle {
  font-size: 12px;
  color: #a0a0a0;
}
.map-markers-list {
  width: 320px;
  border-left: 1px solid #f0f2f4;
  overflow-y: auto;
  padding: 12px;
}
.map-marker-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}
.map-marker-item:hover, .map-marker-item.active {
  background: #e8f4fd;
}
.marker-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: white;
}
.marker--visit { background: #2490EF; }
.marker--customer { background: #28a745; }
.marker--rep { background: #9c27b0; }
.marker-info {
  flex: 1;
}
.marker-name {
  font-weight: 600;
  font-size: 13px;
  color: #1f272e;
}
.marker-coords {
  font-size: 11px;
  color: #a0a0a0;
}
.marker-status {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
  text-transform: uppercase;
}
.marker-status.active { background: #e8f5e9; color: #28a745; }
.marker-status.inactive { background: #ffebee; color: #dc3545; }
</style>
