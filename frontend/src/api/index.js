import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from '@/utils/auth'

// 创建 axios 实例
const service = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000',
  timeout: 15000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
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

// API 方法 — 用函数封装，避免模块初始化时序问题
export const authApi = {
  register: (data) => service.post('/api/auth/register', data),
  login: (data) => service.post('/api/auth/login', data),
  logout: () => service.post('/api/auth/logout')
}

export const userApi = {
  getProfile: () => service.get('/api/users/profile'),
  updateProfile: (data) => service.put('/api/users/profile', data),
  getAddresses: () => service.get('/api/users/addresses'),
  addAddress: (data) => service.post('/api/users/addresses', data),
  updateAddress: (id, data) => service.put(`/api/users/addresses/${id}`, data),
  deleteAddress: (id) => service.delete(`/api/users/addresses/${id}`),
  getPointsLogs: (params) => service.get('/api/users/points', { params }),
  getConsumptionStats: (params) => service.get('/api/users/consumption-stats', { params })
}

export const productApi = {
  getList: (params) => service.get('/api/products', { params }),
  getDetail: (id) => service.get(`/api/products/${id}`),
  getHot: (limit = 10) => service.get('/api/products/hot', { params: { limit } }),
  getNew: (limit = 10) => service.get('/api/products/new', { params: { limit } })
}

export const categoryApi = {
  getList: () => service.get('/api/categories'),
  getDetail: (id) => service.get(`/api/categories/${id}`)
}

export const cartApi = {
  getList: () => service.get('/api/cart'),
  add: (data) => service.post('/api/cart', data),
  update: (id, data) => service.put(`/api/cart/${id}`, data),
  delete: (id) => service.delete(`/api/cart/${id}`),
  clear: () => service.post('/api/cart/clear')
}

export const orderApi = {
  getList: (params) => service.get('/api/orders', { params }),
  getDetail: (id) => service.get(`/api/orders/${id}`),
  create: (data) => service.post('/api/orders', data),
  pay: (id) => service.post(`/api/orders/${id}/pay`),
  cancel: (id) => service.post(`/api/orders/${id}/cancel`),
  receive: (id) => service.post(`/api/orders/${id}/receive`)
}

export const couponApi = {
  getAvailable: () => service.get('/api/coupons/available'),
  getMy: (status) => service.get('/api/coupons/my', { params: { status } }),
  receive: (id) => service.post(`/api/coupons/${id}/receive`)
}

export const reviewApi = {
  getProductReviews: (productId, params) => service.get(`/api/reviews/product/${productId}`, { params }),
  create: (data) => service.post('/api/reviews', data),
  getMy: (params) => service.get('/api/reviews/my', { params })
}

export const adminApi = {
  getUsers: (params) => service.get('/api/admin/users', { params }),
  updateUserStatus: (id, data) => service.put(`/api/admin/users/${id}/status`, data),
  setUserVip: (id, data) => service.put(`/api/admin/users/${id}/vip`, data),
  getOrders: (params) => service.get('/api/admin/orders', { params }),
  shipOrder: (id, data) => service.post(`/api/admin/orders/${id}/ship`, data),
  getStatsOverview: () => service.get('/api/admin/stats/overview'),
  getHotProducts: (limit) => service.get('/api/admin/stats/hot-products', { params: { limit } }),
  getSalesTrend: (days) => service.get('/api/admin/stats/sales-trend', { params: { days } }),
  createProduct: (data) => service.post('/api/products', data),
  updateProduct: (id, data) => service.put(`/api/products/${id}`, data),
  deleteProduct: (id) => service.delete(`/api/products/${id}`),
  createCategory: (data) => service.post('/api/categories', data)
}

// 兼容旧引用：统一导出 api 对象
export const api = {
  auth: authApi,
  user: userApi,
  product: productApi,
  category: categoryApi,
  cart: cartApi,
  order: orderApi,
  coupon: couponApi,
  review: reviewApi,
  admin: adminApi
}

export default service
