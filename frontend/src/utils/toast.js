import { ref, createApp, defineComponent, h } from 'vue'

const toasts = ref([])
let idCounter = 0

export function toast(message, type = 'info', duration = 4000) {
  const id = ++idCounter
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, duration)
}

export function successToast(msg) { toast(msg, 'success') }
export function errorToast(msg) { toast(msg, 'error') }

export { toasts }
