<template>
  <div class="space-y-8 max-w-2xl">
    <div>
      <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Settings</h1>
      <p class="text-gray-500 mt-1">Configure break, overtime rules, and global app settings.</p>
    </div>
    
    <div class="p-6 bg-white rounded-xl shadow-md border border-gray-100 flex flex-col space-y-6">
      <div v-if="successMsg" class="p-4 bg-green-100 text-green-800 rounded-lg shadow">
        {{ successMsg }}
      </div>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Default Break Time (Hours)</label>
          <input 
            type="number" 
            step="0.5" 
            v-model="formData.default_break_time" 
            class="w-full border border-gray-300 rounded-md shadow-sm px-4 py-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Default Work Hours (Hours)</label>
          <input 
            type="number" 
            step="0.5" 
            v-model="formData.default_work_hours" 
            class="w-full border border-gray-300 rounded-md shadow-sm px-4 py-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
      </div>
      
      <div class="pt-4 border-t border-gray-100">
        <Button variant="solid" @click="saveSettings" :loading="isSaving">
          Save Settings
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button, createResource } from 'frappe-ui'

const formData = ref({
  default_break_time: 1.5,
  default_work_hours: 8.0
})
const isSaving = ref(false)
const successMsg = ref('')

const settingsRes = createResource({
  url: 'attendance_plus.api.settings.get_settings',
  method: 'GET',
  auto: true,
  onSuccess: (data) => {
    formData.value.default_break_time = data.default_break_time || 1.5
    formData.value.default_work_hours = data.default_work_hours || 8.0
  }
})

const saveRes = createResource({
  url: 'attendance_plus.api.settings.save_settings'
})

const saveSettings = async () => {
  isSaving.value = true
  successMsg.value = ''
  try {
    await saveRes.submit({ data: JSON.stringify(formData.value) })
    successMsg.value = 'Settings saved successfully!'
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (e) {
    console.error("Save failed", e)
  } finally {
    isSaving.value = false
  }
}
</script>
