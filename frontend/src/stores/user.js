import { defineStore } from 'pinia'
import { sessionApi } from '@/api/session-api'
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
      removeToken()
    },

    async ensureSession(force = false) {
      if (!this.token) {
        this.clearAuth()
        return false
      }

      if (!force && this.user) {
        return true
      }

      if (this._ensureSessionPromise) {
        return this._ensureSessionPromise
      }

      this._ensureSessionPromise = sessionApi.user.getProfile()
        .then((user) => {
          this.setUser(user)
          return true
        })
        .catch((error) => {
          const status = error?.response?.status

          if (status === 401 || status === 403 || status === 404) {
            this.clearAuth()
          } else {
            // Hide stale login UI on transient backend or DB failures,
            // but keep the token so a later retry can still succeed.
            this.user = null
          }

          return false
        })
        .finally(() => {
          this._ensureSessionPromise = null
        })

      return this._ensureSessionPromise
    },

    async logout() {
      try {
        if (this.token) {
          await sessionApi.auth.logout()
        }
      } catch (error) {
        // JWT logout is client-side; still clear local auth state.
      }

      this.clearAuth()
    }
  },

  getters: {
    hasToken: (state) => !!state.token,
    isLoggedIn: (state) => !!state.token && !!state.user,
    isAdmin: (state) => state.user?.user_id === 1
  }
})
