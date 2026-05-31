<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Attendance Dashboard</h1>
        <p class="text-gray-500 mt-1">Live metrics and check-in status for today.</p>
      </div>
      <div class="flex space-x-3">
        <Button variant="solid" @click="syncData" :loading="isSyncing" icon-left="refresh-cw">
          Sync Now
        </Button>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="dashboardRes.error" class="p-4 bg-red-100 text-red-800 rounded-lg shadow">
      <strong>Error loading dashboard:</strong> {{ dashboardRes.error.message || dashboardRes.error }}
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="p-6 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-xl flex flex-col items-center justify-center text-white">
        <span class="text-indigo-100 text-sm font-semibold uppercase tracking-wider">Total Employees</span>
        <span class="text-5xl font-black mt-2 drop-shadow-md">
          {{ dashboardRes.data ? dashboardRes.data.total_employees : 0 }}
        </span>
      </div>
      <div class="p-6 bg-gradient-to-br from-emerald-400 to-green-600 rounded-xl shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-xl flex flex-col items-center justify-center text-white">
        <span class="text-emerald-100 text-sm font-semibold uppercase tracking-wider">Present Today</span>
        <span class="text-5xl font-black mt-2 drop-shadow-md">
          {{ dashboardRes.data ? dashboardRes.data.present_today : 0 }}
        </span>
      </div>
      <div class="p-6 bg-gradient-to-br from-rose-400 to-red-600 rounded-xl shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-xl flex flex-col items-center justify-center text-white">
        <span class="text-rose-100 text-sm font-semibold uppercase tracking-wider">Absent Today</span>
        <span class="text-5xl font-black mt-2 drop-shadow-md">
          {{ dashboardRes.data ? dashboardRes.data.absent_today : 0 }}
        </span>
      </div>
      <div class="p-6 bg-gradient-to-br from-blue-400 to-cyan-600 rounded-xl shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-xl flex flex-col items-center justify-center text-white">
        <span class="text-blue-100 text-sm font-semibold uppercase tracking-wider">Pending Approvals</span>
        <span class="text-5xl font-black mt-2 drop-shadow-md">
          {{ dashboardRes.data ? dashboardRes.data.pending_regs : 0 }}
        </span>
      </div>
    </div>
    
    <!-- Live Attendance List -->
    <div class="p-6 bg-white rounded-xl shadow-md border border-gray-100 flex flex-col h-96">
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
          :rows="(dashboardRes.data && dashboardRes.data.live_attendance) ? dashboardRes.data.live_attendance : []"
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, ListView, createResource } from 'frappe-ui'

const isSyncing = ref(false)

const dashboardRes = createResource({
  url: 'attendance_plus.api.dashboard.get_dashboard_data',
  method: 'GET', // Prevents CSRF issues for fetching data
  auto: true
})

const syncRes = createResource({
  url: 'attendance_plus.api.dashboard.trigger_sync' // POST by default, requires CSRF
})

const syncData = async () => {
  isSyncing.value = true
  try {
    await syncRes.fetch()
    await dashboardRes.fetch() // Refresh dashboard data
  } catch (e) {
    console.error("Sync failed", e)
  } finally {
    isSyncing.value = false
  }
}
</script>
