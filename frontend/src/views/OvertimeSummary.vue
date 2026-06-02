<template>
  <div class="space-y-8 h-full flex flex-col">
    <div>
      <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Overtime Summary</h1>
      <p class="text-gray-500 mt-1">View and analyze daily overtime reports.</p>
    </div>
    
    <div class="flex-grow bg-white rounded-xl shadow-md border border-gray-100 flex flex-col overflow-hidden">
      <ListView
        :columns="[
          { label: 'Employee', key: 'employee_name', width: '25%' },
          { label: 'Date', key: 'attendance_date', width: '15%' },
          { label: 'In Time', key: 'in_time_fmt', width: '20%' },
          { label: 'Out Time', key: 'out_time_fmt', width: '20%' },
          { label: 'OT Hours', key: 'custom_overtime_hours', width: '20%' }
        ]"
        :rows="formattedData"
        row-key="name"
        :selectable="false"
        class="h-full"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ListView, createResource } from 'frappe-ui'

const otRes = createResource({
  url: 'attendance_plus.api.overtime.get_overtime_summary',
  method: 'GET',
  auto: true
})

const formattedData = computed(() => {
  if (!otRes.data) return []
  return otRes.data.map(row => ({
    ...row,
    in_time_fmt: row.in_time ? row.in_time.substring(11, 16) : '-',
    out_time_fmt: row.out_time ? row.out_time.substring(11, 16) : '-'
  }))
})
</script>
