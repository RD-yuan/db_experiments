// Vue CLI's dev bundling trips over axios' ESM helpers; use the browser CJS build for stable runtime behavior.
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
    // Token cleanup is enough if the store cannot be loaded yet.
  }
}

function redirectToLogin() {
  if (typeof window === 'undefined' || window.location.pathname === '/login') {
    return
  }

  const redirect = `${window.location.pathname}${window.location.search}`
  const query = redirect && redirect !== '/login'
    ? `?redirect=${encodeURIComponent(redirect)}`
    : ''

  window.location.href = `/login${query}`
}

request.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      if (res.code === 401) {
        clearClientSession()
        redirectToLogin()
      }
      return Promise.reject(new Error(res.message || 'Error'))
    }
    return res.data
  },
  error => {
    let msg = error.response?.data?.message || ''
    const status = error.response?.status
    const requestUrl = error.config?.url || ''

    if (!msg) {
      if (error.code === 'ECONNABORTED') {
        msg = '请求超时，请检查后端服务和远程数据库连通性'
      } else if (error.message === 'Network Error') {
        msg = '无法连接后端服务，或后端无法访问远程数据库'
      } else {
        msg = error.message || '网络错误'
      }
    }

    if (status === 401 || (status === 404 && requestUrl.includes('/api/users/profile'))) {
      clearClientSession()

      if (status === 401) {
        redirectToLogin()
      }
    }

    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

const api = {
  auth: {
    register: (data) => request.post('/api/auth/register', data),
    login: (data) => request.post('/api/auth/login', data),
    logout: () => request.post('/api/auth/logout')
  },

  user: {
    getProfile: () => request.get('/api/users/profile'),
    updateProfile: (data) => request.put('/api/users/profile', data),
    getAddresses: () => request.get('/api/users/addresses'),
    addAddress: (data) => request.post('/api/users/addresses', data),
    updateAddress: (id, data) => request.put(`/api/users/addresses/${id}`, data),
    deleteAddress: (id) => request.delete(`/api/users/addresses/${id}`),
    getPointsLogs: (params) => request.get('/api/users/points', { params }),
    getConsumptionStats: (params) => request.get('/api/users/consumption-stats', { params }),
    recharge: (data) => request.post('/api/users/recharge', data)
  },

  product: {
    getList: (params) => request.get('/api/products', { params }),
    getDetail: (id) => request.get(`/api/products/${id}`),
    getHot: (limit = 10) => request.get('/api/products/hot', { params: { limit } }),
    getNew: (limit = 10) => request.get('/api/products/new', { params: { limit } })
  },

  category: {
    getList: () => request.get('/api/categories'),
    getDetail: (id) => request.get(`/api/categories/${id}`)
  },

  cart: {
    getList: () => request.get('/api/cart'),
    add: (data) => request.post('/api/cart', data),
    update: (id, data) => request.put(`/api/cart/${id}`, data),
    delete: (id) => request.delete(`/api/cart/${id}`),
    clear: () => request.post('/api/cart/clear')
  },

  order: {
    getList: (params) => request.get('/api/orders', { params }),
    getDetail: (id) => request.get(`/api/orders/${id}`),
    create: (data) => request.post('/api/orders', data),
    pay: (id) => request.post(`/api/orders/${id}/pay`),
    cancel: (id) => request.post(`/api/orders/${id}/cancel`),
    receive: (id) => request.post(`/api/orders/${id}/receive`)
  },

  coupon: {
    getAvailable: () => request.get('/api/coupons/available'),
    getMy: (status) => request.get('/api/coupons/my', { params: { status } }),
    receive: (id) => request.post(`/api/coupons/${id}/receive`)
  },

  review: {
    getProductReviews: (productId, params) => request.get(`/api/reviews/product/${productId}`, { params }),
    create: (data) => request.post('/api/reviews', data),
    update: (id, data) => request.put(`/api/reviews/${id}`, data),
    delete: (id) => request.delete(`/api/reviews/${id}`),
    getMy: (params) => request.get('/api/reviews/my', { params })
  },

  admin: {
    getUsers: (params) => request.get('/api/admin/users', { params }),
    updateUserStatus: (id, data) => request.put(`/api/admin/users/${id}/status`, data),
    setUserVip: (id, data) => request.put(`/api/admin/users/${id}/vip`, data),
    getOrders: (params) => request.get('/api/admin/orders', { params }),
    shipOrder: (id, data) => request.post(`/api/admin/orders/${id}/ship`, data),
    getStatsOverview: () => request.get('/api/admin/stats/overview'),
    getHotProducts: (limit) => request.get('/api/admin/stats/hot-products', { params: { limit } }),
    getSalesTrend: (days) => request.get('/api/admin/stats/sales-trend', { params: { days } }),
    getProducts: (params) => request.get('/api/admin/products', { params }),
    createProduct: (data) => request.post('/api/products', data),
    updateProduct: (id, data) => request.put(`/api/products/${id}`, data),
    deleteProduct: (id) => request.delete(`/api/products/${id}`),
    createCategory: (data) => request.post('/api/categories', data),
    offShelfProduct: (id) => request.put(`/api/admin/products/${id}/off-shelf`),
    onShelfProduct: (id) => request.put(`/api/products/${id}`, { status: 1 }), // 上架
    deleteProductPermanently: (id) => request.delete(`/api/admin/products/${id}/permanent`),
  }
}

export { api }
export default request
