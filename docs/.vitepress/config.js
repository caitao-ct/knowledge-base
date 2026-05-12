import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '前端知识库',
  description: '前端组件、业务规则、编码规范',
  lang: 'zh-CN',
  themeConfig: {
    nav: [
      { text: '业务场景', link: '/业务场景/' },
      { text: 'UI 组件', link: '/UI组件/' },
      { text: '编码规范', link: '/编码规范/' },
    ],
    sidebar: {
      '/业务场景/': [
        { text: '概述', link: '/业务场景/' },
        { text: '订单流程', link: '/业务场景/订单流程' },
        { text: '支付规则', link: '/业务场景/支付规则' },
      ],
      '/UI组件/': [
        { text: '概述', link: '/UI组件/' },
        { text: 'Button 按钮', link: '/UI组件/Button' },
        { text: 'DataTable 表格', link: '/UI组件/DataTable' },
        { text: 'Form 表单', link: '/UI组件/Form' },
      ],
      '/编码规范/': [
        { text: '概述', link: '/编码规范/' },
        { text: 'Vue 风格指南', link: '/编码规范/vue-style-guide' },
        { text: '命名规范', link: '/编码规范/命名规范' },
      ],
    },
  },
})
