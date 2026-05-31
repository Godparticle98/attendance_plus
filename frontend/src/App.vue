<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6 bg-gray-50 min-h-screen">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">Attendance Plus Dashboard</h1>
      <Button variant="solid" @click="refreshData">Refresh</Button>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="p-4 bg-white rounded shadow-sm border border-gray-100 flex flex-col items-center justify-center">
        <span class="text-gray-500 text-sm font-medium">Total Employees</span>
        <span class="text-3xl font-bold text-gray-800 mt-2">{{ totalEmployees }}</span>
      </div>
      <div class="p-4 bg-white rounded shadow-sm border border-green-100 flex flex-col items-center justify-center">
        <span class="text-gray-500 text-sm font-medium">Present Today</span>
        <span class="text-3xl font-bold text-green-600 mt-2">{{ presentToday }}</span>
      </div>
      <div class="p-4 bg-white rounded shadow-sm border border-red-100 flex flex-col items-center justify-center">
        <span class="text-gray-500 text-sm font-medium">Absent Today</span>
        <span class="text-3xl font-bold text-red-600 mt-2">{{ absentToday }}</span>
      </div>
      <div class="p-4 bg-white rounded shadow-sm border border-blue-100 flex flex-col items-center justify-center">
        <span class="text-gray-500 text-sm font-medium">Pending Regularizations</span>
        <span class="text-3xl font-bold text-blue-600 mt-2">{{ pendingRegs }}</span>
      </div>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="md:col-span-2 p-6 bg-white rounded shadow-sm border border-gray-100">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Today's Attendance</h2>
        <!-- List component for attendance -->
        <ListView
          :columns="[
            { label: 'Employee', key: 'employee_name', width: '30%' },
            { label: 'Status', key: 'status', width: '20%' },
            { label: 'In Time', key: 'in_time', width: '25%' },
            { label: 'Out Time', key: 'out_time', width: '25%' }
          ]"
          :rows="attendanceRows"
          row-key="name"
        />
      </div>

      <div class="p-6 bg-white rounded shadow-sm border border-gray-100">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Quick Links</h2>
        <ul class="space-y-3">
          <li>
            <a href="/app/attendance-regularization" class="text-blue-600 hover:underline flex items-center">
               Approve Regularizations
            </a>
          </li>
          <li>
            <a href="/app/query-report/Daily%20Overtime%20Summary" class="text-blue-600 hover:underline flex items-center">
               Daily Overtime Summary
            </a>
          </li>
          <li>
            <a href="/app/attendance-plus-settings" class="text-blue-600 hover:underline flex items-center">
               Attendance Plus Settings
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button, ListView, createResource } from 'frappe-ui'

const totalEmployees = ref(0)
const presentToday = ref(0)
const absentToday = ref(0)
const pendingRegs = ref(0)
const attendanceRows = ref([])

const getToday = () => {
  return new Date().toISOString().split('T')[0]
}

const employeesRes = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'Employee',
      filters: { status: 'Active' },
      limit_page_length: 0
    }
  }
})

const attendanceRes = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'Attendance',
      filters: { attendance_date: getToday() },
      fields: ['name', 'employee_name', 'status', 'in_time', 'out_time'],
      limit_page_length: 50
    }
  }
})

const regsRes = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'Attendance Regularization',
      filters: { status: 'Pending Approval' },
      limit_page_length: 0
    }
  }
})

const refreshData = async () => {
  const [emps, atts, regs] = await Promise.all([
    employeesRes.fetch(),
    attendanceRes.fetch(),
    regsRes.fetch()
  ])
  
  totalEmployees.value = emps.length || 0
  
  const present = atts.filter(a => a.status === 'Present' || a.status === 'Half Day')
  const absent = atts.filter(a => a.status === 'Absent')
  
  presentToday.value = present.length
  absentToday.value = absent.length
  
  // Format times for display
  attendanceRows.value = atts.map(a => ({
    ...a,
    in_time: a.in_time ? a.in_time.split(' ')[1] : '-',
    out_time: a.out_time ? a.out_time.split(' ')[1] : '-'
  }))
  
  pendingRegs.value = regs.length || 0
}

onMounted(() => {
  refreshData()
})
</script>
