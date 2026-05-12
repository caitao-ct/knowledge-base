# Button 按钮

## 引入

```vue
import { Button } from '@/components/ui/button'
```

## Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| variant | `'primary' \| 'secondary' \| 'danger' \| 'ghost'` | `'primary'` | 按钮风格 |
| size | `'sm' \| 'md' \| 'lg'` | `'md'` | 按钮尺寸 |
| loading | `boolean` | `false` | 加载态 |
| disabled | `boolean` | `false` | 禁用 |
| icon | `string` | — | 图标名称 |

## 用法示例

```vue
<template>
  <Button variant="primary" @click="handleSubmit">
    提交订单
  </Button>
  <Button variant="danger" :loading="isDeleting" @click="handleDelete">
    删除
  </Button>
  <Button variant="ghost" size="sm" icon="search">
    搜索
  </Button>
</template>
```

## 业务规则

1. **支付相关页面**只能用 `variant="primary"`
2. **删除操作**必须加二次确认弹窗 (`ElMessageBox.confirm`)
3. `loading` 时按钮自动 `disabled`，阻止重复提交
4. **表单提交按钮**必须加 `loading` 状态
