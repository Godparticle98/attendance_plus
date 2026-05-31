<template>
  <div class="p-8 max-w-7xl mx-auto space-y-8 bg-gray-50 min-h-screen">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Attendance Plus Dashboard</h1>
        <p class="text-gray-500 mt-1">Live metrics and check-in status for today.</p>
      </div>
      <div class="flex space-x-3">
        <Button variant="solid" @click="syncData" :loading="isSyncing" icon-left="refresh-cw">
          Sync Now
        </Button>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="p-6 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-xl flex flex-col items-center justify-center text-white">
        <span class="text-indigo-100 text-sm font-semibold uppercase tracking-wider">Total Employees</span>
        <span class="text-5xl font-black mt-2 drop-shadow-md">{{ metrics.total_employees || 0 }}</span>
      </div>
      <div class="p-6 bg-gradient-to-br from-emerald-400 to-green-600 rounded-xl shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-xl flex flex-col items-center justify-center text-white">
        <span class="text-emerald-100 text-sm font-semibold uppercase tracking-wider">Present Today</span>
        <span class="text-5xl font-black mt-2 drop-shadow-md">{{ metrics.present_today || 0 }}</span>
      </div>
      <div class="p-6 bg-gradient-to-br from-rose-400 to-red-600 rounded-xl shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-xl flex flex-col items-center justify-center text-white">
        <span class="text-rose-100 text-sm font-semibold uppercase tracking-wider">Absent Today</span>
        <span class="text-5xl font-black mt-2 drop-shadow-md">{{ metrics.absent_today || 0 }}</span>
      </div>
      <div class="p-6 bg-gradient-to-br from-blue-400 to-cyan-600 rounded-xl shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-xl flex flex-col items-center justify-center text-white">
        <span class="text-blue-100 text-sm font-semibold uppercase tracking-wider">Pending Approvals</span>
        <span class="text-5xl font-black mt-2 drop-shadow-md">{{ metrics.pending_regs || 0 }}</span>
      </div>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Live Attendance List -->
      <div class="md:col-span-2 p-6 bg-white rounded-xl shadow-md border border-gray-100 flex flex-col">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-bold text-gray-800">Live Check-ins Today</h2>
          <span class="flex h-3 w-3 relative">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
        </div>
        
        <div class="flex-grow overflow-auto">
          <ListView
            :columns="[
              { label: 'Employee', key: 'employee_name', width: '30%' },
              { label: 'Status', key: 'status', width: '30%' },
              { label: 'First In', key: 'in_time', width: '20%' },
              { label: 'Last Out', key: 'out_time', width: '20%' }
            ]"
            :rows="metrics.live_attendance || []"
            row-key="employee_name"
          >
            <template #cell(status)="{ row }">
              <span 
                class="px-2 py-1 rounded-full text-xs font-semibold"
                :class="{
                  'bg-green-100 text-green-800': row.status === 'Present',
                  'bg-blue-100 text-blue-800': row.status === 'Punched IN',
                  'bg-orange-100 text-orange-800': row.status === 'Punched OUT'
                }"
              >
                {{ row.status }}
              </span>
            </template>
          </ListView>
        </div>
      </div>

      <!-- Quick Links -->
      <div class="p-6 bg-white rounded-xl shadow-md border border-gray-100 h-fit">
        <h2 class="text-xl font-bold text-gray-800 mb-6">Operations</h2>
        <div class="space-y-4">
          <a href="/app/attendance-regularization" class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition border border-transparent hover:border-gray-200 group">
            <div class="h-10 w-10 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 group-hover:scale-110 transition">
              <svg xmlns="http://www.w3.org/-svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-semibold text-gray-800">Approve Regularizations</p>
              <p class="text-xs text-gray-500">Review missing punches</p>
            </div>
          </a>
          
          <a href="/app/query-report/Daily%20Overtime%20Summary" class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition border border-transparent hover:border-gray-200 group">
            <div class="h-10 w-10 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 group-hover:scale-110 transition">
              <svg xmlns="http://www.w3.org/-svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-semibold text-gray-800">Overtime Summary</p>
              <p class="text-xs text-gray-500">View daily OT reports</p>
            </div>
          </a>
          
          <a href="/app/attendance-plus-settings" class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition border border-transparent hover:border-gray-200 group">
            <div class="h-10 w-10 bg-slate-100 rounded-full flex items-center justify-center text-slate-600 group-hover:scale-110 transition">
              <svg xmlns="http://www.w3.org/-svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-semibold text-gray-800">Settings</p>
              <p class="text-xs text-gray-500">Configure break and OT rules</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button, ListView, createResource } from 'frappe-ui'

const metrics = ref({})
const isSyncing = ref(false)

const dashboardRes = createResource({
  url: 'attendance_plus.api.dashboard.get_dashboard_data'
})

const syncRes = createResource({
  url: 'attendance_plus.api.dashboard.trigger_sync'
})

const fetchMetrics = async () => {
  try {
    const data = await dashboardRes.fetch()
    if (data) {
      metrics.value = data.message || data
    }
  } catch (e) {
    console.error("Failed to fetch metrics", e)
  }
}

const syncData = async () => {
  isSyncing.value = true
  try {
    await syncRes.fetch()
    await fetchMetrics()
  } catch (e) {
    console.error("Sync failed", e)
  } finally {
    isSyncing.value = false
  }
}

onMounted(() => {
  fetchMetrics()
})
</script>

<style>
/* Custom animations handled by Tailwind classes (e.g. animate-ping, scale-105) */
</style>
