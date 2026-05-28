/**
 * useDateRange — shared composable for validated date range filters
 * Provides: dateFrom, dateTo, dateError, setFrom, setTo, validateRange
 */
import { ref, computed } from 'vue'
import dayjs from 'dayjs'

export function useDateRange(defaultDays = 30) {
  const dateFrom = ref(dayjs().subtract(defaultDays, 'day').format('YYYY-MM-DD'))
  const dateTo   = ref(dayjs().format('YYYY-MM-DD'))
  const dateError = ref('')

  function validateRange() {
    if (!dateFrom.value || !dateTo.value) {
      dateError.value = ''
      return true
    }
    if (dayjs(dateTo.value).isBefore(dayjs(dateFrom.value))) {
      dateError.value = 'End date cannot be before start date'
      return false
    }
    if (dayjs(dateTo.value).diff(dayjs(dateFrom.value), 'day') > 365) {
      dateError.value = 'Range cannot exceed 1 year'
      return false
    }
    dateError.value = ''
    return true
  }

  function setFrom(val, onValid) {
    dateFrom.value = val
    if (dateTo.value && dayjs(dateTo.value).isBefore(dayjs(val))) {
      // Auto-correct: push dateTo forward to match dateFrom
      dateTo.value = val
    }
    dateError.value = ''
    if (validateRange() && onValid) onValid()
  }

  function setTo(val, onValid) {
    if (dateFrom.value && dayjs(val).isBefore(dayjs(dateFrom.value))) {
      dateError.value = 'End date cannot be before start date'
      return // Don't update, reject the input
    }
    dateTo.value = val
    dateError.value = ''
    if (validateRange() && onValid) onValid()
  }

  function reset(days = defaultDays) {
    dateFrom.value = dayjs().subtract(days, 'day').format('YYYY-MM-DD')
    dateTo.value = dayjs().format('YYYY-MM-DD')
    dateError.value = ''
  }

  const rangeLabel = computed(() => {
    if (!dateFrom.value || !dateTo.value) return ''
    if (dateFrom.value === dateTo.value) return dayjs(dateFrom.value).format('D MMM YYYY')
    return `${dayjs(dateFrom.value).format('D MMM')} – ${dayjs(dateTo.value).format('D MMM YYYY')}`
  })

  return { dateFrom, dateTo, dateError, setFrom, setTo, validateRange, reset, rangeLabel }
}
