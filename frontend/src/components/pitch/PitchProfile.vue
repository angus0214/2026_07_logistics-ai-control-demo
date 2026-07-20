<script setup lang="ts">
import { Mail, FileText, Github, Linkedin, CodeXml } from 'lucide-vue-next'
</script>

<template>
  <section class="py-24 px-6 lg:px-16 bg-gray-900 text-gray-300 border-t border-gray-800">
    <div class="max-w-4xl mx-auto flex flex-col items-center text-center space-y-10">
      
      <!-- Profile Header -->
      <div class="space-y-4">
        <div class="w-20 h-20 bg-gradient-to-tr from-blue-500 to-indigo-500 rounded-2xl mx-auto flex items-center justify-center shadow-lg shadow-blue-500/20 rotate-3 hover:rotate-0 transition-transform">
          <CodeXml class="w-10 h-10 text-white" />
        </div>
        <h2 class="text-3xl md:text-4xl font-extrabold text-white mt-6">Built by Angus Wu</h2>
        <p class="text-blue-400 font-medium tracking-wide uppercase text-sm">
          Forward Deployed Engineer / Solutions Architect
        </p>
      </div>

      <!-- Core Philosophy (FDE Mindset) -->
      <div class="bg-gray-800/50 p-8 rounded-2xl border border-gray-700/50 max-w-2xl relative">
        <div class="absolute -top-4 -left-2 text-6xl text-gray-700 font-serif opacity-50">"</div>
        <p class="text-lg text-gray-400 leading-relaxed italic relative z-10">
          我致力於將前沿的 AI 技術，轉化為能解決企業真實痛點的落地產品。我相信最好的架構不是追求最酷炫的技術，而是能在不破壞既有核心的前提下，實現最優雅的軟著陸。
        </p>
        <div class="absolute -bottom-8 -right-2 text-6xl text-gray-700 font-serif opacity-50">"</div>
      </div>

      <!-- Call to Action / Contact Links -->
      <div class="flex flex-wrap justify-center gap-4 pt-6">
        
        <!-- Resume Link -->
        <a 
          href="/resume.pdf" 
          target="_blank"
          class="flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-full font-medium transition-colors shadow-lg shadow-blue-900/50"
        >
          <FileText class="w-5 h-5" />
          <span>View Resume</span>
        </a>

        <!-- Email Link -->
        <a 
          href="mailto:anguswu0214@gmail.com" 
          class="flex items-center space-x-2 bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 px-6 py-3 rounded-full font-medium transition-colors"
        >
          <Mail class="w-5 h-5 text-gray-400" />
          <span>Contact Me</span>
        </a>

        <!-- LinkedIn Link -->
        <a 
          href="https://www.linkedin.com/in/angus-wu-879155167/" 
          target="_blank"
          class="flex items-center space-x-2 bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 px-6 py-3 rounded-full font-medium transition-colors"
        >
          <Linkedin class="w-5 h-5 text-gray-400" />
          <span>LinkedIn</span>
        </a>

        <!-- GitHub Link -->
        <a 
          href="https://github.com/angus0214" 
          target="_blank"
          class="flex items-center space-x-2 bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 px-6 py-3 rounded-full font-medium transition-colors"
        >
          <Github class="w-5 h-5 text-gray-400" />
          <span>GitHub</span>
        </a>

      </div>

    </div>
  </section>
</template>
