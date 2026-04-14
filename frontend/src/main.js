import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import { pinia } from './stores'
import { useUserStore } from './stores/user'
import './assets/styles/main.scss'

const app = createApp(App)
const userStore = useUserStore(pinia)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

window.addEventListener('focus', () => {
  if (userStore.hasToken) {
    userStore.ensureSession(true)
  }
})

userStore.ensureSession(true).finally(() => {
  app.mount('#app')
})
