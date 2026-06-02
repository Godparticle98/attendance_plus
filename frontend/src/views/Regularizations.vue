<template>
  <div class="space-y-8 h-full flex flex-col">
    <div>
      <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Approve Regularizations</h1>
      <p class="text-gray-500 mt-1">Review and approve missing punches.</p>
    </div>
    
    <div class="flex-grow bg-white rounded-xl shadow-md border border-gray-100 flex flex-col overflow-hidden">
      <ListView
        :columns="[
          { label: 'Employee', key: 'employee_name', width: '20%' },
          { label: 'Date', key: 'date', width: '15%' },
          { label: 'Type', key: 'regularization_type', width: '25%' },
          { label: 'Reason', key: 'reason', width: '25%' },
          { label: 'Action', key: 'action', width: '15%' }
        ]"
        :rows="regsRes.data || []"
        row-key="name"
        :selectable="false"
        class="h-full"
      >
        <template #cell(action)="{ row }">
          <Button size="sm" variant="solid" @click="approve(row.name)">
            Approve
          </Button>
        </template>
      </ListView>
    </div>
  </div>
</template>

<script setup>
import { ListView, Button, createResource } from 'frappe-ui'

const regsRes = createResource({
  url: 'attendance_plus.api.regularization.get_pending_regularizations',
  method: 'GET',
  auto: true
})

const approveRes = createResource({
  url: 'attendance_plus.api.regularization.approve_regularization'
})

const approve = async (name) => {
  await approveRes.submit({ name })
  regsRes.fetch() // Refresh list after approval
}
</script>
