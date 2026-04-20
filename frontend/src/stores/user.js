import { defineStore } from 'pinia'
import { api } from '@/api'
import { getToken, setToken as persistToken, removeToken } from '@/utils/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: getToken() || null,
    _ensureSessionPromise: null
  }),

  actions: {
    setUser(user) {
      this.user = user || null
    },

    setToken(token) {
      this.token = token || null

      if (token) {
        persistToken(token)
      } else {
        removeToken()
      }
    },

    setAuth(authData) {
      this.setToken(authData?.token || null)
      this.setUser(authData?.user || null)
    },

    clearAuth() {
      this.user = null
      this.token = null
      this._ensureSessionPromise = null
      removeToken()
    },

    async ensureSession(force = false) {
      if (!this.token) {
        this.clearAuth()
        return { ok: false, reason: 'missing-token' }
      }

      if (!force && this.user) {
        return { ok: true, reason: 'cached' }
      }

      if (this._ensureSessionPromise) {
        return this._ensureSessionPromise
      }

      const previousUser = this.user

      this._ensureSessionPromise = api.user.getProfile()
        .then((user) => {
          this.setUser(user)
          return { ok: true, reason: 'validated' }
        })
        .catch((error) => {
          const status = error?.response?.status

          if (status === 401 || status === 403 || status === 404) {
            this.clearAuth()
            return { ok: false, reason: 'invalid' }
          } else {
            this.user = previousUser
            return { ok: false, reason: 'unreachable' }
          }
        })
        .finally(() => {
          this._ensureSessionPromise = null
        })

      return this._ensureSessionPromise
    },

    async logout() {
      try {
        if (this.token) {
          await api.auth.logout()
        }
      } catch (error) {
        // JWT logout is client-side; still clear local auth state.
      }

      this.clearAuth()
    }
  },

  getters: {
    hasToken: (state) => !!state.token,
    hasUser: (state) => !!state.user,
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.user_id === 1
  }
})
