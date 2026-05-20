<template>
  <div class="notifications-page">
    <el-card>
      <template #header><div style="display:flex;justify-content:space-between;align-items:center"><span>消息中心</span><el-button size="small" @click="readAll" :disabled="unreadCount===0">全部已读</el-button></div></template>
      <div v-loading="loading">
        <div v-for="n in list" :key="n.id" class="notif-item" :class="{ unread: !n.is_read }" @click="markRead(n)">
          <div class="notif-header"><el-tag :type="n.type===1?'':'info'" size="small">{{ n.type===1?'公告':'个人' }}</el-tag><span class="notif-title">{{ n.title }}</span><span class="notif-time">{{ n.create_time?.slice(0,16) }}</span></div>
          <div class="notif-content" v-if="n.content">{{ n.content }}</div>
        </div>
        <el-empty v-if="list.length===0 && !loading" description="暂无消息" />
      </div>
      <el-pagination v-if="total>0" v-model:current-page="page" :page-size="20" :total="total" layout="total,prev,pager,next" @current-change="load" style="margin-top:20px;justify-content:center" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/api'
const loading = ref(false), list = ref([]), page = ref(1), total = ref(0), unreadCount = ref(0)
const load = async () => {
  loading.value = true
  try {
    const r = await api.notification.getList({ page: page.value })
    list.value = r.items
    total.value = r.total
  } catch(e){console.error(e)}
  loading.value = false
}
const loadUnread = async () => {
  try {
    const r = await api.notification.getUnreadCount()
    if (r) unreadCount.value = r.count
  } catch(e){console.error(e)}
}
const markRead = async (n) => {
  if (n.is_read) return
  try {
    await api.notification.markRead(n.id)
    n.is_read = 1
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch(e){console.error(e)}
}
const readAll = async () => {
  try {
    await api.notification.readAll()
    list.value.forEach(n => n.is_read = 1)
    unreadCount.value = 0
  } catch(e){console.error(e)}
}
onMounted(() => { load(); loadUnread() })
</script>

<style lang="scss" scoped>
.notifications-page { max-width:800px; margin:0 auto; padding:20px; }
.notif-item { padding:15px; border-bottom:1px solid #f0f0f0; cursor:pointer; }
.notif-item.unread { background:#f0f9ff; }
.notif-item:hover { background:#f5f7fa; }
.notif-header { display:flex; align-items:center; gap:10px; }
.notif-title { font-weight:500; flex:1; }
.notif-time { color:#999; font-size:12px; }
.notif-content { margin-top:10px; color:#666; font-size:13px; }
</style>
