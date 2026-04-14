import axios from 'axios/dist/browser/axios.cjs'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from '@/utils/auth'

const request = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '',
  timeout: 15000
})

async function clearClientSession() {
  removeToken()

  try {
    const [{ pinia }, { useUserStore }] = await Promise.all([
      import('@/stores'),
      import('@/stores/user')
    ])
    useUserStore(pinia).clearAuth()
  } catch (error) {
    // Removing the token is enough if the store is not ready yet.
  }
}

request.interceptors.request.use(
  (config) => {
    const token = getToken()

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => {
    const payload = response.data
    const code = payload?.code ?? response.status
    const message = payload?.message || 'Request failed'

    if (code !== 200) {
      if (code === 401 || code === 403) {
        clearClientSession()
      }

      ElMessage.error(message)
      return Promise.reject(new Error(message))
    }

    return payload.data
  },
  async (error) => {
    const status = error?.response?.status
    const requestUrl = error?.config?.url || ''
    let message = error?.response?.data?.message || ''

    if (!message) {
      if (error?.code === 'ECONNABORTED') {
        message = 'Request timed out. Check the backend service and remote database connection.'
      } else if (error?.message === 'Network Error') {
        message = 'Cannot reach the backend service, or the backend cannot reach the remote database.'
      } else {
        message = error?.message || 'Network error'
      }
    }

    if (status === 401 || status === 403 || (status === 404 && requestUrl.includes('/api/users/profile'))) {
      await clearClientSession()
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export const sessionApi = {
  auth: {
    login: (data) => request.post('/api/auth/login', data),
    register: (data) => request.post('/api/auth/register', data),
    logout: () => request.post('/api/auth/logout')
  },
  user: {
    getProfile: () => request.get('/api/users/profile')
  }
}

export default request
