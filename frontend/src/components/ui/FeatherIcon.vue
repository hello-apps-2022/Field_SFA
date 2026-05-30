<template>
  <svg
    class="feather"
    :class="[`feather-${name}`, $attrs.class]"
    xmlns="http://www.w3.org/2000/svg"
    width="24" height="24" viewBox="0 0 24 24"
    fill="none" stroke="currentColor"
    stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
    v-html="iconHtml"
  />
</template>

<script setup>
import { computed } from 'vue'
import feather from 'feather-icons'

const props = defineProps({ name: { type: String, required: true } })

// Icons not in the feather set (Lucide-style / custom) kept as overrides.
const extra = {
  'grip-vertical': '<circle cx="9" cy="5" r="1"/><circle cx="9" cy="12" r="1"/><circle cx="9" cy="19" r="1"/><circle cx="15" cy="5" r="1"/><circle cx="15" cy="12" r="1"/><circle cx="15" cy="19" r="1"/>',
  'receipt': '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1-2-1Z"></path><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"></path><path d="M12 17.5v-11"></path>',
}

const iconHtml = computed(() => {
  if (extra[props.name]) return extra[props.name]
  const icon = feather.icons[props.name]
  return icon ? icon.contents : '<circle cx="12" cy="12" r="10"></circle>'
})
</script>
