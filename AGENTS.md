# Agent Guidelines

本文件用于约束 AI 在本仓库中的开发行为。目标是在实现需求时保持代码健壮、风格一致、边界清晰，并避免引入不必要的复杂度。

## General Rules

- 所有文件读写使用 UTF-8 编码；修改文件时不要改变原有编码。
- Always keep Chinese content unchanged.
- 修改前先阅读相关代码、配置和已有约定，避免凭空重写或引入与项目不一致的实现。
- 优先复用现有依赖、组件、工具函数、接口封装和目录结构，除非确有必要，不新增第三方库。
- 变更应尽量小而明确，避免无关重构、格式化整仓文件或修改与当前任务无关的内容。
- 对外部库、框架、SDK、API、CLI 工具或云服务的用法有疑问时，优先使用 Context7 MCP 查询最新官方文档。

## Development Workflow

1. 明确需求边界，识别涉及的前端、后端、数据模型、权限或测试范围。
2. 阅读相关文件，确认现有模式后再实现。
3. 按职责拆分代码，保持页面编排、业务组件、通用工具、接口模型分层清晰。
4. 实现后按影响范围运行校验，并根据结果修复问题。
5. 总结变更时说明改了什么、验证了什么，以及仍存在的风险或未验证项。

## Current Project Structure

- `apps/web` 是 Next.js App Router 前端项目：
  - `app/layout.tsx` 只放根布局、全局 provider、全局样式和全局 toaster。
  - `app/(app)/layout.tsx` 是登录后后台系统布局，统一包裹 `AuthGate` 和 `AppShell`。
  - `app/(app)/loading.tsx`、`app/(app)/error.tsx` 是后台区域的路由级加载和错误边界。
  - `app/(app)/**/page.tsx` 只作为页面入口，组合对应 feature 组件，不直接承载请求、复杂状态和 CRUD 逻辑。
  - `app/login/page.tsx` 是独立登录页，不应被后台 `AppShell` 包裹。
  - `src/components` 放跨业务共享组件，`src/components/ui` 放通用基础 UI。
  - `src/features/<domain>` 放业务模块，例如 `assets`、`tasks`、`roles`、`users`；模块内优先按 `api.ts`、`components/`、必要的 `permissions.ts` 或业务工具拆分。
  - `src/lib/api.ts` 是唯一前端 API client 入口，`src/lib/auth.tsx` 是唯一认证状态入口，`src/lib/types.ts` 放共享接口类型。
- `apps/api` 是 FastAPI 后端项目：
  - `app/<domain>/routes.py`、`service.py`、`repository.py` 按领域组织业务。
  - `app/core` 放配置、数据库、安全、权限、错误、初始化等通用能力。
  - `app/models.py` 放 SQLAlchemy 模型，`app/schemas.py` 放接口 schema。
- `deploy`、`docs`、`storage` 分别放部署配置、项目文档和本地持久化文件。

## Robustness Requirements

- 处理用户输入、接口返回、空数据、异常状态、权限状态和加载状态，避免只覆盖理想路径。
- 保持类型定义准确，避免使用不必要的 `any`、隐式结构或重复定义接口。
- 异步逻辑应处理失败、取消、重复请求或竞态风险，错误信息应可追踪且不泄露敏感数据。
- API 返回结构、分页结构、权限依赖和 `response_model` 应保持一致。
- 修改数据库模型时，同步考虑 schema、迁移、默认值、兼容性和测试。
- 不把请求、状态管理、表单逻辑和展示逻辑全部堆在单个文件中。

## Frontend Guidelines

- 修改 `apps/web` 中的代码时，优先查看：
  - `apps/web/package.json`：确认已安装依赖和项目技术栈。
  - `apps/web/app/globals.css`：了解全局样式、颜色、间距、字体和 Tailwind 变量。
- `apps/web` 使用 Next.js App Router：页面放在 `app/`，共享组件和工具放在 `src/components`、`src/lib`，业务模块放在 `src/features/<domain>`。
- 受保护后台页面必须放在 `app/(app)` route group 下，由 `app/(app)/layout.tsx` 统一处理 `AuthGate`、`AppShell`、侧边栏、顶部栏和系统级布局。
- 业务 `page.tsx` 应保持轻量：只导入并渲染 feature 组件；不要在 `page.tsx` 中直接写 `useEffect`、`useState`、API 请求、表格列定义、弹窗编排或复杂权限判断。
- 业务请求封装在 `src/features/<domain>/api.ts`，业务 UI 放在 `src/features/<domain>/components`，权限判断或领域工具放在同一 feature 的独立文件中。
- 新增 UI 优先复用已有 Tailwind 变量、`src/components/ui` 和布局组件。
- 前端请求统一经过 `src/lib/api.ts`，认证状态统一经过 `src/lib/auth.tsx`，避免在页面中重复封装 token 和请求逻辑。
- 可复用、职责清晰、逻辑较独立的 UI 或业务模块应抽离为独立组件。
- 页面应覆盖加载、空状态、错误状态、禁用状态、权限不足和响应式布局；后台区域优先复用 `app/(app)/loading.tsx`、`app/(app)/error.tsx`，组件内部仍需处理业务级加载和错误状态。
- 能作为 Server Component 的 `page.tsx` 不要加 `"use client"`；只在需要浏览器状态、事件、effect、localStorage 或上下文 hook 的组件文件中使用 `"use client"`。
- 不要把 `AppShell`、`AuthGate` 等系统布局组件写进业务组件或业务页面；系统布局只在 layout 层组合。

## Backend Guidelines

- `apps/api` 使用 FastAPI：业务路由按模块放在 `app/<domain>/routes.py`，通用能力放在 `app/core`。
- 数据模型集中在 `apps/api/app/models.py`，接口结构集中在 `apps/api/app/schemas.py`。
- 后端接口应保持 `response_model`、权限依赖、分页返回结构一致。
- 新增或调整权限时，同步更新 `apps/api/app/core/permissions.py`，并检查 `apps/api/app/core/seeding.py` 的初始化数据和相关路由保护。
- 业务逻辑应避免散落在路由函数中；复杂逻辑优先抽入服务层或清晰的辅助函数。
- 输入校验、异常处理、事务边界和数据库查询性能应随功能一起考虑。

## Backend Layering Rules

- 新增或修改后端业务时，默认采用 `routes.py`、`service.py`、`repository.py` 三层结构。
- `routes.py` 只负责 HTTP 层：路由声明、依赖注入、权限依赖、请求参数解析、响应模型和把业务异常转换为 HTTP 异常。
- `service.py` 负责业务层：业务规则、跨表/跨资源编排、事务提交、状态变更、文件存储等副作用协调。
- `repository.py` 负责数据访问层：封装 SQLAlchemy 查询、计数、分页、按 ID/唯一键读取和新增对象，不在路由中直接写查询。
- 路由函数中不要直接调用 `select()`、`db.scalars()`、`db.add()`、`db.commit()` 等数据库操作；除 `Depends(get_db)` 外，数据库会话应传入 service/repository 使用。
- 业务异常优先使用 `app/core/errors.py` 中的业务异常类型，由路由层转换为 HTTP 响应，避免 service 层直接依赖 FastAPI 的 `HTTPException`。
- 每个领域模块优先保持自包含，例如 `app/users/routes.py`、`app/users/service.py`、`app/users/repository.py`；跨领域复用逻辑放在 `app/core` 或明确的共享模块。
- 新增业务接口时，应同步考虑对应 service/repository 测试；至少保证路由层、业务层和数据访问层职责没有重新混在一起。

## Testing And Validation

- 提交前按影响范围运行校验：
  - 前端优先运行 `pnpm typecheck` 和 `pnpm biome:check`。
  - 后端优先运行 `uv run pytest`。
- 新增复杂逻辑、权限规则、数据模型或接口行为时，应补充相应测试。
- 无法运行校验时，应明确说明原因和未覆盖风险。
- 修复 bug 时优先补充能复现问题的测试，避免只改表面现象。

## Do Not

- 不要随意翻译、替换或改写已有中文内容。
- 不要绕过 `src/lib/api.ts` 或 `src/lib/auth.tsx` 重复实现前端请求和认证逻辑。
- 不要无必要引入新依赖、新框架或新的全局状态方案。
- 不要为了通过检查而删除测试、降低类型约束或隐藏错误。
- 不要提交未解释的大范围重构、无关格式化或与需求无关的文件变更。
