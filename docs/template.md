# 模板说明

这个仓库是一个 AI/后台管理类全栈快速开发模板，保留登录、角色权限、任务中心、文件存储、数据库迁移、Docker Compose 和管理台壳子。

## 技术栈

- 前端：Next.js 15、React 19、TypeScript、Tailwind CSS v4、lucide-react、sonner、pnpm
- 后端：FastAPI、Pydantic Settings、SQLAlchemy 2.x、Alembic、uv、pytest
- 基础设施：Docker Compose、PostgreSQL、独立 API/Web Dockerfile、storage volume、healthcheck

## 默认账号

- 用户名：`admin`
- 密码：`admin123456`

请在正式项目中修改默认账号、`SECRET_KEY` 和权限初始化逻辑。
