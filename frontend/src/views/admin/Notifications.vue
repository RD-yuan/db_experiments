<template>
  <div class="admin-notifs">
    <el-card>
      <template #header><div style="display:flex;justify-content:space-between;align-items:center"><span>消息管理</span><el-button type="primary" size="small" @click="openDialog()">发布消息</el-button></div></template>
      <el-table :data="list" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column label="类型" width="100"><template #default="{row}"><el-tag :type="row.type===1?'':'info'" size="small">{{ row.type===1?'公告':'个人消息' }}</el-tag></template></el-table-column>
        <el-table-column prop="create_time" label="时间" width="170"><template #default="{row}">{{ row.create_time?.slice(0,16) }}</template></el-table-column>
      </el-table>
      <el-pagination v-if="total>0" v-model:current-page="page" :page-size="20" :total="total" layout="total,prev,pager,next" @current-change="load" style="margin-top:20px;justify-content:flex-end" />
    </el-card>

    <el-dialog v-model="dialog" title="发布消息" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="类型"><el-radio-group v-model="form.type"><el-radio :value="1">系统公告</el-radio><el-radio :value="2">个人消息</el-radio></el-radio-group></el-form-item>
        <el-form-item v-if="form.type===2" label="用户ID"><el-input-number v-model="form.user_id" :min="1" /></el-form-item>
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="4" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="publish">发布</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
const loading = ref(false)
const list = ref([])
const page = ref(1)
const total = ref(0)
const dialog = ref(false)
const form = ref({ type: 1, user_id: null, title: '', content: '' })

const load = async () => {
  loading.value = true
  try {
    const r = await api.admin.getNotifications({ page: page.value })
    list.value = r.items
    total.value = r.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const openDialog = () => {
  form.value = { type: 1, user_id: null, title: '', content: '' }
  dialog.value = true
}

const publish = async () => {
  if (!form.value.title) {
    ElMessage.warning('请输入标题')
    return
  }
  try {
    await api.admin.createNotification(form.value)
    ElMessage.success('发布成功')
    dialog.value = false
    load()
  } catch (e) {
    console.error(e)
  }
}

onMounted(load)
</script>
