<script setup lang="ts">
import { ref, provide } from 'vue'
import OpIngestionView from './OpIngestionView.vue'
import DashboardView from './DashboardView.vue'
import BossDashboard from '../components/ui/BossDashboard.vue'

const currentView = ref('op') // 'op', 'db', or 'boss'
provide('currentView', currentView)
</script>

<template>
  <OpIngestionView v-if="currentView === 'op'" />
  <DashboardView v-else-if="currentView === 'db'" />
  <BossDashboard v-else-if="currentView === 'boss'" />
</template>
