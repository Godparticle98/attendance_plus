import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { setConfig, frappeRequest } from 'frappe-ui'

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.mount('#app')
