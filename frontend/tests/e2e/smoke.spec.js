const { test, expect } = require('@playwright/test')

test('user can register, browse products, and add one item to cart', async ({ page }) => {
  const uniqueSuffix = `${Date.now()}`.slice(-6)
  const username = `e2e_${uniqueSuffix}`
  const email = `${username}@example.com`
  const phone = `139${`${Date.now()}`.slice(-8)}`
  const password = '123456'

  await page.goto('/products')
  await expect(page).toHaveURL(/\/products$/)
  await expect(page.getByText('E2E 测试商品')).toBeVisible()

  await page.goto('/cart')
  await expect(page).toHaveURL(/\/login\?redirect=(\/|%2F)cart/)

  await page.goto('/register')
  const textInputs = page.locator('input[type="text"]')
  await textInputs.nth(0).fill(username)
  await textInputs.nth(1).fill(phone)
  await textInputs.nth(2).fill(email)

  const passwordInputs = page.locator('input[type="password"]')
  await passwordInputs.nth(0).fill(password)
  await passwordInputs.nth(1).fill(password)

  await Promise.all([
    page.waitForResponse((response) => {
      return response.url().includes('/api/auth/register') &&
        response.request().method() === 'POST' &&
        response.ok()
    }),
    page.locator('.register-form .el-button--primary').click()
  ])

  await expect(page).toHaveURL(/\/home$/)
  await expect(page.getByText(username)).toBeVisible()

  await page.goto('/products')
  await page.getByText('E2E 测试商品').click()
  await expect(page).toHaveURL(/\/product\/\d+$/)
  await expect(page.getByRole('heading', { name: 'E2E 测试商品' })).toBeVisible()

  await Promise.all([
    page.waitForResponse((response) => {
      return response.url().includes('/api/cart') &&
        response.request().method() === 'POST' &&
        response.ok()
    }),
    page.locator('.action-buttons .el-button--primary').click()
  ])

  await page.goto('/cart')
  await expect(page).toHaveURL(/\/cart$/)
  await expect(page.getByText('E2E 测试商品')).toBeVisible()
})
