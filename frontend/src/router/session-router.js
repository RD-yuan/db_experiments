import { createRouter, createWebHistory } from 'vue-router'
import { pinia } from '@/stores'
import { useUserStore } from '@/stores/user'

const APP_TITLE = 'Ecommerce Platform'

const routes = [
  {
    path: '/',
    component: () => import('@/views/layout/SessionMainLayout.vue'),
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/home/Index.vue'),
        meta: { title: 'Home' }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/product/List.vue'),
        meta: { title: 'Products' }
      },
      {
        path: 'product/:id',
        name: 'ProductDetail',
        component: () => import('@/views/product/Detail.vue'),
        meta: { title: 'Product Detail' }
      },
      {
        path: 'cart',
        name: 'Cart',
        component: () => import('@/views/cart/Index.vue'),
        meta: { title: 'Cart', requiresAuth: true }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/order/List.vue'),
        meta: { title: 'Orders', requiresAuth: true }
      },
      {
        path: 'order/:id',
        name: 'OrderDetail',
        component: () => import('@/views/order/Detail.vue'),
        meta: { title: 'Order Detail', requiresAuth: true }
      },
      {
        path: 'user',
        component: () => import('@/views/user/Center.vue'),
        meta: { title: 'User Center', requiresAuth: true },
        redirect: '/user/profile',
        children: [
          {
            path: 'profile',
            name: 'Profile',
            component: () => import('@/views/user/Profile.vue'),
            meta: { title: 'Profile', requiresAuth: true }
          },
          {
            path: 'addresses',
            name: 'Addresses',
            component: () => import('@/views/user/Addresses.vue'),
            meta: { title: 'Addresses', requiresAuth: true }
          },
          {
            path: 'stats',
            name: 'ConsumptionStats',
            component: () => import('@/views/user/Stats.vue'),
            meta: { title: 'Stats', requiresAuth: true }
          },
          {
            path: 'coupons',
            name: 'MyCoupons',
            component: () => import('@/views/user/Coupons.vue'),
            meta: { title: 'Coupons', requiresAuth: true }
          }
        ]
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/SessionLoginPage.vue'),
    meta: { title: 'Login' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/SessionRegisterPage.vue'),
    meta: { title: 'Register' }
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/SessionAdminShell.vue'),
    meta: { title: 'Admin', requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: 'Dashboard', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/admin/Users.vue'),
        meta: { title: 'Users', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'products',
        name: 'ProductManagement',
        component: () => import('@/views/admin/Products.vue'),
        meta: { title: 'Products', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'orders',
        name: 'OrderManagement',
        component: () => import('@/views/admin/Orders.vue'),
        meta: { title: 'Orders', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'coupons',
        name: 'CouponManagement',
        component: () => import('@/views/admin/Coupons.vue'),
        meta: { title: 'Coupons', requiresAuth: true, requiresAdmin: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: 'Not Found' }
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

  if (userStore.hasToken) {
    await userStore.ensureSession(true)
  }

  if (requiresAuth && !userStore.isLoggedIn) {
    return {
      path: '/login',
      query: { redirect: to.fullPath }
    }
  }

  if ((to.path === '/login' || to.path === '/register') && userStore.isLoggedIn) {
    return typeof to.query.redirect === 'string' ? to.query.redirect : '/'
  }

  if (requiresAdmin && !userStore.isAdmin) {
    return '/'
  }

  return true
})

export default router
