<template>
  <div class="flex h-full flex-col items-center justify-center gap-4 text-ink-gray-4">
    <FeatherIcon name="alert-circle" class="h-12 w-12" />
    <p class="text-lg font-semibold text-ink-gray-7">Page not found</p>
    <Button size="sm" @click="$router.push('/dashboard')">Go to Dashboard</Button>
  </div>
</template>
