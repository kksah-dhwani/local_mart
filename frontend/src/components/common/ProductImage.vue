<template>
  <div :class="['relative bg-gray-100 overflow-hidden', containerClass]">
    <!-- Actual image -->
    <img
      v-if="!failed && src"
      :src="src"
      :alt="alt"
      :class="['w-full h-full object-cover transition-opacity duration-300', loaded ? 'opacity-100' : 'opacity-0', imgClass]"
      @load="loaded = true"
      @error="failed = true"
      referrerpolicy="no-referrer"
      crossorigin="anonymous"
    />

    <!-- Skeleton while loading -->
    <div
      v-if="!loaded && !failed && src"
      class="absolute inset-0 bg-gray-200 animate-pulse"
    ></div>

    <!-- Fallback — shown when no src OR image fails to load -->
    <div
      v-if="failed || !src"
      class="absolute inset-0 flex flex-col items-center justify-center gap-1 text-gray-400 bg-gray-100"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <span v-if="showLabel" class="text-xs">No Image</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  alt: { type: String, default: '' },
  containerClass: { type: String, default: 'aspect-square' },
  imgClass: { type: String, default: '' },
  showLabel: { type: Boolean, default: false },
})

const loaded = ref(false)
const failed = ref(false)

// Reset state when src changes
watch(() => props.src, () => {
  loaded.value = false
  failed.value = false
})
</script>
