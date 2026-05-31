<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden font-sans">
    
    <!-- Sidebar -->
    <aside class="w-64 bg-white shadow-xl border-r border-gray-100 flex flex-col transition-all duration-300 z-10 hidden md:flex">
      <div class="h-16 flex items-center px-6 border-b border-gray-100">
        <div class="flex items-center space-x-3">
          <div class="h-8 w-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-md">
            A+
          </div>
          <span class="text-xl font-extrabold text-gray-900 tracking-tight">Attendance+</span>
        </div>
      </div>
      
      <div class="flex-1 overflow-y-auto py-6 px-4 space-y-2">
        <p class="px-2 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Main Menu</p>
        
        <router-link to="/" class="nav-item group" active-class="active-nav-item">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3 text-gray-400 group-hover:text-indigo-600 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
          Dashboard
        </router-link>
        
        <router-link to="/regularizations" class="nav-item group" active-class="active-nav-item">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3 text-gray-400 group-hover:text-indigo-600 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Regularizations
        </router-link>

        <router-link to="/overtime" class="nav-item group" active-class="active-nav-item">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3 text-gray-400 group-hover:text-indigo-600 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Overtime Summary
        </router-link>

        <router-link to="/settings" class="nav-item group" active-class="active-nav-item">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3 text-gray-400 group-hover:text-indigo-600 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Settings
        </router-link>
      </div>
      
      <div class="p-4 border-t border-gray-100">
        <a href="/app" class="flex items-center text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Desk
        </a>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 overflow-y-auto focus:outline-none">
      <!-- Mobile Header -->
      <header class="md:hidden bg-white shadow-sm h-16 flex items-center justify-between px-4">
        <div class="flex items-center space-x-2">
           <div class="h-8 w-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-md">
            A+
          </div>
          <span class="text-xl font-bold text-gray-900">Attendance+</span>
        </div>
        <a href="/app" class="text-sm text-indigo-600 font-medium">Desk</a>
      </header>

      <div class="p-4 md:p-8 max-w-7xl mx-auto">
        <!-- Router View will render the active page here -->
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>

  </div>
</template>

<script setup>
</script>

<style>
.nav-item {
  @apply flex items-center px-4 py-3 text-sm font-medium rounded-lg text-gray-600 hover:bg-indigo-50 hover:text-indigo-700 transition-colors;
}

.active-nav-item {
  @apply bg-indigo-50 text-indigo-700;
}

.active-nav-item svg {
  @apply text-indigo-700;
}

/* Page Transition Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>
