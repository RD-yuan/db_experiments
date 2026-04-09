import { defineStore } from 'pinia'
import { getToken } from '@/utils/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: getToken() || null
  }),

  actions: {
    setUser(user) {
      this.user = user
    },

    setToken(token) {
      this.token = token
    },

    logout() {
      this.user = null
      this.token = null
    }
  },

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin'
  }
})
