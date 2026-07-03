<script setup lang="ts">
import { ref, provide } from 'vue'
import OpIngestionView from './views/OpIngestionView.vue'
import DashboardView from './views/DashboardView.vue'

const currentView = ref('op') // 'op' or 'db'
provide('currentView', currentView)
</script>

<template>
  <OpIngestionView v-if="currentView === 'op'" />
  <DashboardView v-else-if="currentView === 'db'" />
</template>
