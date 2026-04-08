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
    
    // 根据业务状态码处理
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      
      // 401: Token 过期
      if (res.code === 401) {
        removeToken()
        location.href = '/login'
      }
      
      return Promise.reject(new Error(res.message || 'Error'))
    }
    
    return res.data
  },
  error => {
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default service

// API 方法封装
export const api = {
  // 认证
  auth: {
    register: (data) => service.post('/api/auth/register', data),
    login: (data) => service.post('/api/auth/login', data),
    logout: () => service.post('/api/auth/logout')
  },
  
  // 用户
  user: {
    getProfile: () => service.get('/api/users/profile'),
    updateProfile: (data) => service.put('/api/users/profile', data),
    getAddresses: () => service.get('/api/users/addresses'),
    addAddress: (data) => service.post('/api/users/addresses', data),
    updateAddress: (id, data) => service.put(`/api/users/addresses/${id}`, data),
    deleteAddress: (id) => service.delete(`/api/users/addresses/${id}`),
    getPointsLogs: (params) => service.get('/api/users/points', { params }),
    getConsumptionStats: (params) => service.get('/api/users/consumption-stats', { params })
  },
  
  // 商品
  product: {
    getList: (params) => service.get('/api/products', { params }),
    getDetail: (id) => service.get(`/api/products/${id}`),
    getHot: (limit = 10) => service.get('/api/products/hot', { params: { limit } }),
    getNew: (limit = 10) => service.get('/api/products/new', { params: { limit } })
  },
  
  // 分类
  category: {
    getList: () => service.get('/api/categories'),
    getDetail: (id) => service.get(`/api/categories/${id}`)
  },
  
  // 购物车
  cart: {
    getList: () => service.get('/api/cart'),
    add: (data) => service.post('/api/cart', data),
    update: (id, data) => service.put(`/api/cart/${id}`, data),
    delete: (id) => service.delete(`/api/cart/${id}`),
    clear: () => service.post('/api/cart/clear')
  },
  
  // 订单
  order: {
    getList: (params) => service.get('/api/orders', { params }),
    getDetail: (id) => service.get(`/api/orders/${id}`),
    create: (data) => service.post('/api/orders', data),
    pay: (id) => service.post(`/api/orders/${id}/pay`),
    cancel: (id) => service.post(`/api/orders/${id}/cancel`),
    receive: (id) => service.post(`/api/orders/${id}/receive`)
  },
  
  // 优惠券
  coupon: {
    getAvailable: () => service.get('/api/coupons/available'),
    getMy: (status) => service.get('/api/coupons/my', { params: { status } }),
    receive: (id) => service.post(`/api/coupons/${id}/receive`)
  },
  
  // 评价
  review: {
    getProductReviews: (productId, params) => service.get(`/api/reviews/product/${productId}`, { params }),
    create: (data) => service.post('/api/reviews', data),
    getMy: (params) => service.get('/api/reviews/my', { params })
  },
  
  // 管理员
  admin: {
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
}
