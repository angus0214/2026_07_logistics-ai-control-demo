<script setup lang="ts">
import PitchHero from '../components/pitch/PitchHero.vue'
import PitchGenesis from '../components/pitch/PitchGenesis.vue'
import PitchArchitecture from '../components/pitch/PitchArchitecture.vue'
import PitchFlywheel from '../components/pitch/PitchFlywheel.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-800 font-sans selection:bg-blue-200">
    <PitchHero />
    <PitchGenesis />
    <PitchArchitecture />
    <PitchFlywheel />
    
    <!-- Placeholder for upcoming sections -->
    <div class="py-20 text-center text-gray-500 bg-white">
      More technical details coming soon... (Scroll down)
    </div>
  </div>
</template>

<style scoped>
/* Pitch-specific global styles if any */
</style>
