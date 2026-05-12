# DataTable 表格

## 引入

```vue
import { DataTable } from '@/components/ui/data-table'
```

## Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| columns | `Column[]` | `[]` | 列配置 |
| data | `Record[]` | `[]` | 数据源 |
| loading | `boolean` | `false` | 加载态 |
| pagination | `object` | `{ page:1, size:20 }` | 分页配置 |
| selection | `'none' \| 'single' \| 'multiple'` | `'none'` | 选择模式 |
| sortable | `boolean` | `true` | 是否允许排序 |

## Column 配置

| 属性 | 类型 | 说明 |
|------|------|------|
| key | `string` | 数据字段名 |
| title | `string` | 表头文字 |
| width | `number` | 列宽（px） |
| align | `'left' \| 'center' \| 'right'` | 对齐方式 |
| render | `(row) => VNode` | 自定义渲染 |
| sortable | `boolean` | 当前列可排序 |

## 用法示例

```vue
<template>
  <DataTable
    :columns="columns"
    :data="orderList"
    :loading="loading"
    :pagination="pagination"
    selection="multiple"
    @selection-change="handleSelection"
    @page-change="handlePageChange"
  />
</template>

<script setup>
const columns = [
  { key: 'orderNo', title: '订单号', width: 180 },
  { key: 'amount', title: '金额', align: 'right' },
  { key: 'status', title: '状态', render: (row) => h(OrderStatus, { status: row.status }) },
  { key: 'createdAt', title: '创建时间', sortable: true },
  { key: 'actions', title: '操作', width: 150, render: (row) => h(TableActions, { row }) },
]
</script>
```

## 业务规则

1. **金额列**统一右对齐，保留两位小数
2. **状态列**用 `<OrderStatus>` 组件展示颜色标签
3. 表格默认每页 20 条
4. 超过 10000 条数据需提示"数据量过大，建议筛选后查看"
