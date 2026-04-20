<template>
  <div class="home-page">
    <div class="home-shell">
      <section class="hero-section">
        <el-carousel height="440px" indicator-position="outside" trigger="click">
          <el-carousel-item v-for="(banner, index) in banners" :key="banner.title">
            <div class="banner" :style="{ background: colors[index] }">
              <div class="banner-pattern banner-pattern-grid" />
              <div class="banner-pattern banner-pattern-wave" />
              <div class="banner-orb banner-orb-left" />
              <div class="banner-orb banner-orb-right" />

              <div class="banner-content">
                <span class="banner-badge">{{ banner.badge }}</span>
                <h1>{{ banner.title }}</h1>
                <p>{{ banner.subtitle }}</p>

                <div class="banner-actions">
                  <el-button class="banner-cta" type="primary" size="large" @click="goToProducts">
                    立即选购
                    <el-icon class="button-icon">
                      <ArrowRight />
                    </el-icon>
                  </el-button>

                  <div class="banner-tip">
                    <el-icon>
                      <ShoppingBag />
                    </el-icon>
                    <span>{{ banner.tip }}</span>
                  </div>
                </div>
              </div>

              <div class="banner-panel">
                <div class="panel-chip">{{ banner.panelLabel }}</div>
                <div class="panel-title">{{ banner.panelTitle }}</div>
                <div class="panel-subtitle">{{ banner.panelSubtitle }}</div>

                <div class="panel-stats">
                  <div class="panel-stat">
                    <strong>{{ banner.stats[0].value }}</strong>
                    <span>{{ banner.stats[0].label }}</span>
                  </div>
                  <div class="panel-stat">
                    <strong>{{ banner.stats[1].value }}</strong>
                    <span>{{ banner.stats[1].label }}</span>
                  </div>
                  <div class="panel-stat">
                    <strong>{{ banner.stats[2].value }}</strong>
                    <span>{{ banner.stats[2].label }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </section>

      <section class="products-section">
        <div class="section-header">
          <div class="section-heading">
            <span class="section-accent" />
            <div>
              <p class="section-kicker">Editor Picks</p>
              <h2>热门商品</h2>
            </div>
          </div>
          <p class="section-desc">为你精选高人气单品，轻量视觉与顺滑交互同时在线。</p>
        </div>

        <el-row :gutter="24">
          <el-col
            v-for="(item, index) in products"
            :key="item.id"
            :xs="24"
            :sm="12"
            :md="12"
            :lg="6"
          >
            <el-card
              class="product-card"
              :body-style="{ padding: '0' }"
              shadow="never"
              :style="{ '--delay': `${index * 0.08}s` }"
              @click="viewProduct(item.id)"
            >
              <div class="product-media">
                <span class="product-tag">{{ item.tag }}</span>
                <div class="product-glow" />
                <div class="product-placeholder">
                  <el-icon>
                    <ShoppingBag />
                  </el-icon>
                </div>

                <button
                  class="cart-button"
                  type="button"
                  aria-label="查看商品"
                  @click.stop="viewProduct(item.id)"
                >
                  <el-icon>
                    <ShoppingCart />
                  </el-icon>
                </button>
              </div>

              <div class="product-body">
                <div class="product-caption">{{ item.caption }}</div>
                <h3 class="product-name">{{ item.name }}</h3>

                <div class="product-footer">
                  <div class="price-group">
                    <span class="currency">¥</span>
                    <span class="price-value">{{ formatPrice(item.price) }}</span>
                  </div>

                  <span class="product-link">
                    立即查看
                    <el-icon>
                      <ArrowRight />
                    </el-icon>
                  </span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const colors = [
  'linear-gradient(135deg, #c7f0ff 0%, #74b9ff 48%, #4f7dff 100%)',
  'linear-gradient(135deg, #ffe3c7 0%, #ffb88a 45%, #fb7185 100%)',
  'linear-gradient(135deg, #d6f8e7 0%, #7dd3c7 50%, #34a0a4 100%)'
]

const banners = [
  {
    badge: '春季上新',
    title: '欢迎来到电商平台',
    subtitle: '发现更懂生活方式的精选好物，从日常焕新到潮流搭配一步到位。',
    tip: '全场精选满 99 元包邮，会员专享加码礼遇。',
    panelLabel: '今日推荐',
    panelTitle: '轻松逛，放心选',
    panelSubtitle: '细节更轻盈，购物体验也应该更轻盈。',
    stats: [
      { value: '1.2k+', label: '人气商品' },
      { value: '24h', label: '快速发货' },
      { value: '98%', label: '好评反馈' }
    ]
  },
  {
    badge: '限时精选',
    title: '用更亮眼的方式陈列你的爆款',
    subtitle: '柔和渐变与高对比文案结合，让首页首屏更像真正的品牌橱窗。',
    tip: '专题会场与热卖单品同步上线，第一眼就能看到重点。',
    panelLabel: '爆款专区',
    panelTitle: '热卖榜单持续更新',
    panelSubtitle: '品牌精选、限时活动与畅销单品集中展示。',
    stats: [
      { value: '320+', label: '品牌入驻' },
      { value: '15%', label: '限时优惠' },
      { value: '7d', label: '无忧退换' }
    ]
  },
  {
    badge: '品质生活',
    title: '给用户一眼就想点击的首页体验',
    subtitle: '卡片更通透、留白更舒展、交互更明确，兼顾视觉质感与转化效率。',
    tip: '从首页到商品详情，统一建立现代电商的视觉节奏。',
    panelLabel: '视觉升级',
    panelTitle: '现代、干净、明亮',
    panelSubtitle: '保留 Element Plus 基调，同时把首页气质拉高一档。',
    stats: [
      { value: '16px', label: '卡片圆角' },
      { value: '4px', label: '悬停上浮' },
      { value: '0.6s', label: '淡入动效' }
    ]
  }
]

const products = ref([
  { id: 1, name: '轻盈云感运动鞋', price: 99.9, tag: '新品', caption: '舒适出行' },
  { id: 2, name: '极简通勤双肩包', price: 199.9, tag: '热卖', caption: '城市通勤' },
  { id: 3, name: '亲肤柔软针织衫', price: 299.9, tag: '精选', caption: '春日穿搭' },
  { id: 4, name: '智能保温随行杯', price: 399.9, tag: '好评', caption: '生活方式' }
])

const goToProducts = () => {
  router.push('/products')
}

const viewProduct = (id) => {
  router.push(`/product/${id}`)
}

const formatPrice = (price) => {
  const value = Number(price)
  const digits = Number.isInteger(value) ? 0 : 1

  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  })
}
</script>

<style scoped>
.home-page {
  min-height: 100%;
  background:
    radial-gradient(circle at top left, rgba(96, 165, 250, 0.15), transparent 24%),
    linear-gradient(180deg, #f7fbff 0%, #f9fafb 240px, #f9fafb 100%);
  padding: 28px 24px 72px;
  font-family: 'PingFang SC', 'Segoe UI', 'Microsoft YaHei', sans-serif;
}

.home-shell {
  max-width: 1280px;
  margin: 0 auto;
}

.hero-section {
  position: relative;
}

:deep(.el-carousel__container) {
  border-radius: 28px;
  overflow: hidden;
}

:deep(.el-carousel__indicators--outside) {
  margin-top: 16px;
}

:deep(.el-carousel__indicator--outside button) {
  width: 26px;
  height: 6px;
  border-radius: 999px;
  background-color: rgba(148, 163, 184, 0.4);
}

:deep(.el-carousel__indicator.is-active button) {
  background-color: var(--el-color-primary);
}

.banner {
  position: relative;
  height: 100%;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 360px);
  align-items: center;
  gap: 32px;
  padding: 48px 56px;
  color: #ffffff;
}

.banner-pattern,
.banner-orb {
  pointer-events: none;
  position: absolute;
}

.banner-pattern-grid {
  inset: 0;
  opacity: 0.22;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.16) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.16) 1px, transparent 1px);
  background-size: 34px 34px;
  mask-image: linear-gradient(90deg, transparent 0%, rgba(0, 0, 0, 0.9) 18%, rgba(0, 0, 0, 0.95) 100%);
}

.banner-pattern-wave {
  right: -10%;
  bottom: -28%;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 68%);
}

.banner-orb {
  border-radius: 50%;
  filter: blur(2px);
  background: rgba(255, 255, 255, 0.18);
}

.banner-orb-left {
  top: 56px;
  left: 45%;
  width: 84px;
  height: 84px;
}

.banner-orb-right {
  right: 54px;
  top: 42px;
  width: 140px;
  height: 140px;
  background: rgba(255, 255, 255, 0.14);
}

.banner-content,
.banner-panel {
  position: relative;
  z-index: 1;
}

.banner-badge {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.banner-content h1 {
  margin: 22px 0 14px;
  font-size: 44px;
  line-height: 1.12;
  font-weight: 800;
  letter-spacing: 0.01em;
}

.banner-content p {
  max-width: 560px;
  margin: 0;
  font-size: 17px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.9);
}

.banner-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 30px;
  flex-wrap: wrap;
}

.banner-cta {
  height: 48px;
  padding: 0 22px;
  border: none;
  border-radius: 999px;
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.22);
  font-weight: 700;
}

.button-icon {
  font-size: 16px;
  margin-left: 2px;
}

.banner-tip {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 11px 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  font-size: 14px;
  color: rgba(255, 255, 255, 0.95);
}

.banner-panel {
  justify-self: end;
  width: 100%;
  padding: 26px 24px;
  border-radius: 26px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 24px 50px rgba(15, 23, 42, 0.18);
  backdrop-filter: blur(14px);
}

.panel-chip {
  display: inline-flex;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
  font-size: 12px;
  font-weight: 700;
}

.panel-title {
  margin-top: 18px;
  font-size: 30px;
  line-height: 1.2;
  font-weight: 800;
}

.panel-subtitle {
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.86);
}

.panel-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 24px;
}

.panel-stat {
  padding: 14px 12px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.14);
  text-align: center;
}

.panel-stat strong {
  display: block;
  font-size: 20px;
  font-weight: 800;
}

.panel-stat span {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.82);
}

.products-section {
  margin-top: 76px;
}

.section-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 28px;
}

.section-heading {
  display: flex;
  align-items: center;
  gap: 16px;
}

.section-accent {
  position: relative;
  width: 14px;
  height: 42px;
  border-radius: 999px;
  background: linear-gradient(180deg, var(--el-color-primary) 0%, #f97316 100%);
  box-shadow: 0 10px 24px rgba(249, 115, 22, 0.2);
}

.section-accent::after {
  content: '';
  position: absolute;
  left: 18px;
  top: 12px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(249, 115, 22, 0.3);
}

.section-kicker {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--el-color-primary);
}

.section-header h2 {
  margin: 0;
  font-size: 32px;
  line-height: 1.2;
  color: #111827;
}

.section-desc {
  max-width: 420px;
  margin: 0;
  font-size: 15px;
  line-height: 1.8;
  color: #6b7280;
}

.product-card {
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.95);
  border-radius: 16px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
  cursor: pointer;
  transition: transform 0.32s ease, box-shadow 0.32s ease, border-color 0.32s ease;
  animation: fadeUp 0.6s ease both;
  animation-delay: var(--delay);
}

.product-card:hover {
  transform: translateY(-4px);
  border-color: rgba(96, 165, 250, 0.35);
  box-shadow: 0 22px 42px rgba(15, 23, 42, 0.12);
}

.product-media {
  position: relative;
  height: 220px;
  overflow: hidden;
  background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
}

.product-glow {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0) 72%);
  transform: translate(-50%, -50%);
}

.product-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 58px;
  color: rgba(148, 163, 184, 0.9);
}

.product-tag {
  position: absolute;
  left: 16px;
  top: 16px;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  font-size: 12px;
  font-weight: 700;
  color: #334155;
}

.cart-button {
  position: absolute;
  right: 16px;
  bottom: 16px;
  z-index: 1;
  width: 42px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--el-color-primary) 0%, #74b9ff 100%);
  color: #fff;
  box-shadow: 0 14px 28px rgba(64, 158, 255, 0.26);
  opacity: 0;
  transform: translateY(10px) scale(0.96);
  transition: opacity 0.28s ease, transform 0.28s ease, box-shadow 0.28s ease;
  cursor: pointer;
}

.product-card:hover .cart-button {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.cart-button:hover {
  box-shadow: 0 18px 34px rgba(64, 158, 255, 0.34);
}

.product-body {
  padding: 18px 18px 20px;
  background: #ffffff;
}

.product-caption {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #94a3b8;
}

.product-name {
  margin: 10px 0 18px;
  font-size: 18px;
  line-height: 1.5;
  font-weight: 700;
  color: #0f172a;
}

.product-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.price-group {
  display: inline-flex;
  align-items: baseline;
  color: #f97316;
}

.currency {
  margin-right: 4px;
  font-size: 16px;
  font-weight: 700;
}

.price-value {
  display: inline-block;
  font-size: 30px;
  line-height: 1;
  font-weight: 800;
  transition: transform 0.28s ease;
}

.product-card:hover .price-value {
  transform: scale(1.05);
}

.product-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
  color: #64748b;
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1024px) {
  .banner {
    grid-template-columns: 1fr;
    padding: 42px 36px;
  }

  .banner-panel {
    justify-self: start;
    max-width: 420px;
  }

  .section-header {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .home-page {
    padding: 20px 16px 56px;
  }

  .banner {
    padding: 36px 24px;
  }

  .banner-content h1 {
    font-size: 34px;
  }

  .banner-content p {
    font-size: 15px;
  }

  .banner-panel {
    display: none;
  }

  .products-section {
    margin-top: 60px;
  }

  .section-header h2 {
    font-size: 28px;
  }

  .product-media {
    height: 200px;
  }
}
</style>
