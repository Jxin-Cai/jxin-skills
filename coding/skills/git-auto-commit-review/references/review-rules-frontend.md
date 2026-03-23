# 代码审查规则 — 前端（Vue / React / 通用）

前端项目特定的审查规则。仅在项目使用 Vue/React/前端技术栈时加载。

通用规则见 `review-rules.md`。

## 目录

- [组件设计](#组件设计)
- [状态管理](#状态管理)
- [性能](#性能)
- [安全](#安全)
- [样式与可维护性](#样式与可维护性)
- [TypeScript](#typescript)
- [Vue 特定](#vue-特定)
- [React 特定](#react-特定)

---

## 组件设计

1. **组件职责单一（P0）**
   - **原因**：大组件难以复用、测试和维护
   - **反例**：一个组件同时处理数据获取、表单校验、列表渲染和弹窗逻辑
   - **正例**：拆分为容器组件（负责数据）和展示组件（负责 UI）；每个组件做一件事

2. **Props 接口要清晰且最小化（P1）**
   - **原因**：过多的 props 是组件职责不清的信号
   - **反例**：组件接受 15+ 个 props，其中多个布尔 flag 控制不同行为
   - **正例**：props 数量合理（通常 < 8）；用组合模式替代布尔 flag 堆积

3. **避免 prop drilling 超过 3 层（P1）**
   - **原因**：多层传递 props 使中间组件与底层耦合
   - **反例**：祖父组件的数据经 3 个中间组件原样透传到孙组件
   - **正例**：使用 Context/Provide-Inject/状态管理解决跨层传递

## 状态管理

1. **区分本地状态和全局状态（P0）**
   - **原因**：把所有状态放全局会导致过度渲染和难以追踪的数据流
   - **反例**：表单输入值、弹窗开关等局部 UI 状态放在全局 store 中
   - **正例**：UI 状态用组件本地状态；跨组件共享的业务数据用全局 store

2. **禁止直接修改 store 之外的状态（P0）**
   - **原因**：绕过状态管理的修改破坏单向数据流，导致难以追踪的 bug
   - **反例**：直接修改 props 或通过引用修改 store 中的对象
   - **正例**：通过 action/mutation/dispatch 修改状态；props 视为只读

3. **异步状态要有加载/错误/空状态处理（P1）**
   - **原因**：用户看到白屏或静默失败比看到加载动画或错误提示更糟糕
   - **反例**：API 调用只处理成功，无 loading 和 error 状态
   - **正例**：每个异步操作都有 loading、error、empty 三种状态的 UI 反馈

## 性能

1. **列表渲染必须提供稳定的 key（P0）**
   - **原因**：用 index 作为 key 在列表变动时导致错误的 DOM 复用
   - **反例**：`v-for="(item, index)" :key="index"` 或 `list.map((item, i) => <Item key={i} />)`
   - **正例**：使用业务唯一标识作为 key：`:key="item.id"` / `key={item.id}`

2. **避免在渲染路径中做重计算（P1）**
   - **原因**：每次渲染都执行的昂贵运算会导致卡顿
   - **反例**：在模板/render 中对大数组做 filter+sort+map
   - **正例**：使用 computed/useMemo 缓存计算结果

3. **大列表使用虚拟滚动（P1）**
   - **原因**：渲染上千个 DOM 节点严重影响性能
   - **反例**：直接渲染 1000+ 行的表格
   - **正例**：使用虚拟滚动组件（virtual-scroller / react-window 等）

4. **图片和路由使用懒加载（P2）**
   - **原因**：首屏加载过多资源影响用户体验
   - **反例**：所有页面组件和图片在应用启动时同步加载
   - **正例**：路由级懒加载（动态 import）；图片懒加载（loading="lazy" 或 Intersection Observer）

5. **避免不必要的重渲染（P1）**
   - **原因**：频繁的无效重渲染是前端性能问题的常见根源
   - **反例**：父组件状态变更导致所有子组件重渲染；每次渲染都创建新的对象/函数引用
   - **正例**：React 用 memo/useCallback/useMemo 控制引用稳定性；Vue 利用响应式系统的自动追踪

## 安全

1. **禁止使用 innerHTML/v-html/dangerouslySetInnerHTML 渲染用户输入（P0）**
   - **原因**：XSS 攻击的最直接入口
   - **反例**：`v-html="userComment"` 或 `dangerouslySetInnerHTML={{__html: userInput}}`
   - **正例**：使用文本插值；确需 HTML 渲染时先用 DOMPurify 等工具消毒

2. **敏感数据不要存在前端可见位置（P1）**
   - **原因**：localStorage/sessionStorage/全局变量可被用户和浏览器插件读取
   - **反例**：将 access token 存在 localStorage 且永不过期
   - **正例**：token 存 httpOnly cookie；敏感数据通过 API 按需获取

3. **API 请求校验用户权限由后端负责（P1）**
   - **原因**：前端权限判断仅用于 UI 展示，可被绕过
   - **反例**：只在前端隐藏管理员按钮，后端接口无权限校验
   - **正例**：前端控制 UI 可见性，后端强制校验权限

## 样式与可维护性

1. **避免内联样式堆积（P2）**
   - **原因**：内联样式无法复用、无法响应主题变更、增加阅读难度
   - **反例**：`style="margin-top: 12px; padding: 8px 16px; color: #333; font-size: 14px;"`
   - **正例**：使用 CSS class / CSS Modules / Tailwind 等方案；偶尔的动态样式用内联

2. **禁止使用魔法数字做尺寸/间距（P2）**
   - **原因**：散落各处的数字难以统一调整
   - **反例**：`width: 1024px`、`padding: 17px`
   - **正例**：使用设计系统的 token/变量：`var(--spacing-md)`、`theme.space[4]`

## TypeScript

1. **禁止使用 `any` 除非有明确理由（P1）**
   - **原因**：`any` 绕过类型检查，等于放弃 TS 的核心价值
   - **反例**：`const data: any = fetchData()`
   - **正例**：用具体类型、`unknown`（需运行时检查）、或泛型替代

2. **API 响应要有类型定义（P1）**
   - **原因**：未类型化的 API 响应是运行时错误的温床
   - **反例**：`const res = await api.get('/users')` 无类型标注
   - **正例**：定义响应类型：`const res = await api.get<UserListResponse>('/users')`

## Vue 特定

1. **避免在模板中写复杂表达式（P1）**
   - **原因**：模板中的复杂逻辑难以调试和测试
   - **反例**：`{{ items.filter(i => i.active).map(i => i.name).join(', ') }}`
   - **正例**：用 computed 属性封装逻辑，模板中只引用结果

2. **Composition API 要有清晰的逻辑拆分（P1）**
   - **原因**：setup() 中堆积所有逻辑和单个大 Options 对象同样难以维护
   - **反例**：setup() 中 200+ 行，混合了数据获取、表单处理、事件处理
   - **正例**：按功能拆分为 composable（use 函数）

3. **v-if 和 v-for 不要用在同一元素上（P1）**
   - **原因**：Vue 3 中 v-if 优先级高于 v-for，行为容易混淆且可能导致非预期结果
   - **反例**：`<div v-for="item in list" v-if="item.visible">`
   - **正例**：用 computed 预过滤列表，或用 `<template v-for>` 包裹 `v-if`

## React 特定

1. **Hook 调用遵守规则（P0）**
   - **原因**：Hook 依赖调用顺序，违反规则导致难以追踪的 bug
   - **反例**：在条件语句或循环中调用 Hook
   - **正例**：Hook 只在组件顶层或自定义 Hook 中调用

2. **useEffect 依赖数组要完整（P0）**
   - **原因**：遗漏依赖导致闭包陷阱（stale closure），使用过期值
   - **反例**：`useEffect(() => { doSomething(count) }, [])` 而 count 会变化
   - **正例**：依赖数组包含所有在 effect 中引用的响应式值；用 eslint-plugin-react-hooks 辅助检查

3. **避免在 useEffect 中直接修改状态导致无限循环（P0）**
   - **原因**：effect 中 setState → 触发重渲染 → 重新执行 effect → 无限循环
   - **反例**：`useEffect(() => { setData(transform(data)) }, [data])`
   - **正例**：用 useMemo 做派生数据；或在 setState 中使用函数式更新避免依赖
