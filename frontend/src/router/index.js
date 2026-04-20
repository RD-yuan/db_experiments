import { createRouter, createWebHistory } from 'vue-router'
import { pinia } from '@/stores'
import { useUserStore } from '@/stores/user'

const APP_TITLE = '电商平台'
const authPages = new Set(['/login', '/register'])

const routes = [
  {
    path: '/',
    component: () => import('@/views/layout/AppMainLayout.vue'),
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/home/Index.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/product/List.vue'),
        meta: { title: '商品列表' }
      },
      {
        path: 'product/:id',
        name: 'ProductDetail',
        component: () => import('@/views/product/Detail.vue'),
        meta: { title: '商品详情' }
      },
      {
        path: 'cart',
        name: 'Cart',
        component: () => import('@/views/cart/Index.vue'),
        meta: { title: '购物车', requiresAuth: true }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/order/List.vue'),
        meta: { title: '我的订单', requiresAuth: true }
      },
      {
        path: 'order/:id',
        name: 'OrderDetail',
        component: () => import('@/views/order/Detail.vue'),
        meta: { title: '订单详情', requiresAuth: true }
      },
      {
        path: 'user',
        name: 'UserCenter',
        component: () => import('@/views/user/Center.vue'),
        meta: { title: '个人中心', requiresAuth: true },
        redirect: '/user/profile',
        children: [
          {
            path: 'profile',
            name: 'Profile',
            component: () => import('@/views/user/Profile.vue'),
            meta: { title: '个人信息', requiresAuth: true }
          },
          {
            path: 'addresses',
            name: 'Addresses',
            component: () => import('@/views/user/Addresses.vue'),
            meta: { title: '地址管理', requiresAuth: true }
          },
          {
            path: 'stats',
            name: 'ConsumptionStats',
            component: () => import('@/views/user/Stats.vue'),
            meta: { title: '消费统计', requiresAuth: true }
          },
          {
            path: 'coupons',
            name: 'MyCoupons',
            component: () => import('@/views/user/Coupons.vue'),
            meta: { title: '我的优惠券', requiresAuth: true }
          }
        ]
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginPage.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/RegisterPage.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/admin',
    name: 'AdminShell',
    component: () => import('@/views/admin/AdminShell.vue'),
    meta: { title: '管理后台', requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '数据看板', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/admin/Users.vue'),
        meta: { title: '用户管理', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'products',
        name: 'ProductManagement',
        component: () => import('@/views/admin/Products.vue'),
        meta: { title: '商品管理', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'orders',
        name: 'OrderManagement',
        component: () => import('@/views/admin/Orders.vue'),
        meta: { title: '订单管理', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'coupons',
        name: 'CouponManagement',
        component: () => import('@/views/admin/Coupons.vue'),
        meta: { title: '优惠券管理', requiresAuth: true, requiresAdmin: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  document.title = to.meta?.title ? `${to.meta.title} - ${APP_TITLE}` : APP_TITLE

  const userStore = useUserStore(pinia)
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some((record) => record.meta.requiresAdmin)
  const needsSessionHydration = userStore.hasToken &&
    !userStore.hasUser &&
    (requiresAuth || requiresAdmin || authPages.has(to.path))

  let sessionResult = null

  if (needsSessionHydration) {
    sessionResult = await userStore.ensureSession()
  }

  if (requiresAuth && !userStore.hasToken) {
    return {
      path: '/login',
      query: { redirect: to.fullPath }
    }
  }

  if (authPages.has(to.path)) {
    const hasVerifiedSession = userStore.hasUser || sessionResult?.ok

    if (userStore.hasToken && hasVerifiedSession) {
      return typeof to.query.redirect === 'string' ? to.query.redirect : '/'
    }
  }

  if (requiresAdmin) {
    if (!userStore.hasUser && userStore.hasToken) {
      sessionResult = sessionResult || await userStore.ensureSession()

      if (!userStore.hasToken) {
        return {
          path: '/login',
          query: { redirect: to.fullPath }
        }
      }
    }

    if (userStore.hasUser && !userStore.isAdmin) {
      return '/'
    }
  }

  return true
})

export default router
