// Vue CLI's dev bundling trips over axios' ESM helpers; use the browser CJS build for stable runtime behavior.
import axios from 'axios/dist/browser/axios.cjs'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from '@/utils/auth'

// 创建 axios 实例
const request = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000',
  timeout: 15000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      if (res.code === 401) {
        removeToken()
        window.location.href = '/login'
      }
      return Promise.reject(new Error(res.message || 'Error'))
    }
    return res.data
  },
  error => {
    const msg = error.response?.data?.message || error.message || '网络错误'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

// 统一 API 对象——所有方法直接用 request，无交叉引用
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
    getConsumptionStats: (params) => request.get('/api/users/consumption-stats', { params })
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
    createProduct: (data) => request.post('/api/products', data),
    updateProduct: (id, data) => request.put(`/api/products/${id}`, data),
    deleteProduct: (id) => request.delete(`/api/products/${id}`),
    createCategory: (data) => request.post('/api/categories', data)
  }
}

export { api }
export default request
