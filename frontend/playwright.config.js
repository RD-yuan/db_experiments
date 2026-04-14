const { defineConfig } = require('@playwright/test')

const backendPort = 5010
const frontendPort = 4173
const isWindows = process.platform === 'win32'

const backendCommand = isWindows
  ? '..\\.venv\\Scripts\\python.exe ..\\backend\\e2e_server.py'
  : '../.venv/bin/python ../backend/e2e_server.py'

const frontendCommand = isWindows
  ? `cmd /c "set VUE_APP_API_BASE_URL=http://127.0.0.1:${backendPort}&& npm run serve -- --host 127.0.0.1 --port ${frontendPort}"`
  : `VUE_APP_API_BASE_URL=http://127.0.0.1:${backendPort} npm run serve -- --host 127.0.0.1 --port ${frontendPort}`

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 60000,
  expect: {
    timeout: 10000
  },
  fullyParallel: false,
  workers: 1,
  reporter: [
    ['list'],
    ['html', { open: 'never' }]
  ],
  use: {
    baseURL: `http://127.0.0.1:${frontendPort}`,
    headless: true,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  webServer: [
    {
      command: backendCommand,
      url: `http://127.0.0.1:${backendPort}/health`,
      reuseExistingServer: false,
      timeout: 120000,
      stdout: 'pipe',
      stderr: 'pipe'
    },
    {
      command: frontendCommand,
      url: `http://127.0.0.1:${frontendPort}/js/app.js`,
      reuseExistingServer: false,
      timeout: 240000,
      stdout: 'pipe',
      stderr: 'pipe'
    }
  ]
})
