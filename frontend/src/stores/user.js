import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: null
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
    isAdmin: (state) => state.user?.user_id === 1
  }
})
