const backendTarget = process.env.VUE_APP_PROXY_TARGET || 'http://127.0.0.1:5000'

module.exports = {
  devServer: {
    host: '0.0.0.0',
    allowedHosts: 'all',
    proxy: {
      '^/api': {
        target: backendTarget,
        changeOrigin: true
      },
      '^/health': {
        target: backendTarget,
        changeOrigin: true
      },
      '^/apidocs': {
        target: backendTarget,
        changeOrigin: true
      }
    }
  }
}
