# Frontend Design System Instructions

本项目的前端代码必须遵循 Aurora shadcn/Tailwind v4 设计系统。生成、修改页面或组件时，优先使用 `apps/web/app/globals.css` 中定义的 CSS 变量和 Tailwind token，不要硬编码新的品牌色、背景色、边框色或圆角体系。

## Core Stack

- 使用 Tailwind CSS v4 的 CSS-first 配置方式。
- 全局样式入口是 `apps/web/app/globals.css`。
- 保留以下导入顺序：

```css
@import "tailwindcss";
@import "tw-animate-css";
@import "shadcn/tailwind.css";
```

## Color Tokens

使用语义化 token 编写 UI：

- 页面背景：`bg-background`
- 默认文字：`text-foreground`
- 卡片/面板：`bg-card text-card-foreground`
- 弱化区域：`bg-muted text-muted-foreground`
- 主按钮/主操作：`bg-primary text-primary-foreground`
- 次级操作：`bg-secondary text-secondary-foreground`
- 悬停/选中辅助态：`bg-accent text-accent-foreground`
- 边框：`border-border`
- 输入框边框：`border-input`
- 焦点环：`ring-ring` 或 `outline-ring/50`
- 危险操作：`bg-destructive`

Aurora 扩展色只用于图表、状态点、徽标、强调性图形或少量品牌装饰：

- `aurora-blue`
- `aurora-green`
- `aurora-purple`
- `aurora-orange`
- `aurora-navy`
- `aurora-slate`
- `aurora-line`
- `aurora-soft`

## Layout And Components

- 后台、管理台、业务系统界面应保持克制、清晰、信息密度适中。
- 优先使用现有组件：`Button`、`Input`、`AppShell`、`EmptyState`、`Pagination`。
- 页面主结构使用清晰的导航、表格、表单、列表和状态展示，不要生成营销式 hero。
- 卡片只用于独立的信息单元、表格容器、表单容器或空状态，不要层层嵌套卡片。
- 默认圆角使用 Tailwind 语义类：`rounded-md`、`rounded-lg`、`rounded-xl`，对应全局 `--radius`。
- 图标优先使用 `lucide-react`。

## Typography

- 字体使用全局 `font-sans`。
- 标题使用 `font-semibold`，避免过大的展示字号。
- 管理台内文案以功能、状态、动作命名为主，避免宣传语。
- 所有中文内容保持原样，不要随意改写已有中文。

## Dark Mode

- 暗色模式通过 `.dark` 类触发。
- 新增样式必须使用语义 token，确保亮色和暗色都能自动适配。
- 不要只为亮色模式硬编码 `white`、`slate-*`、`blue-*` 等颜色；必要时优先映射到语义 token。

## Interaction

- 可交互元素必须有清晰 hover/focus/disabled 状态。
- 输入框使用 `focus:border-primary`、`focus:ring-2`、`focus:ring-ring/20` 一类 token 化焦点样式。
- 动效可以使用 `tw-animate-css` 提供的动画类，但要保持克制，不影响后台操作效率。

## Do Not

- 不要新增 `tailwind.config.js` 或旧版 Tailwind v3 写法。
- 不要使用 `@tailwind base/components/utilities`。
- 不要引入 `autoprefixer` 或 `postcss-import`。
- 不要新增与 Aurora token 冲突的独立色板。
- 不要把中文文案翻译、替换或改写成英文。
