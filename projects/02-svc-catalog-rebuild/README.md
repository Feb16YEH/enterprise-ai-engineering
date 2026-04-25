# Project Overview
这是一个报表元数据目录服务；核心资源是ReportSepc，支持带鉴权的CRUD
使用 FastAPI + SQLModel + SQLite

# Resource Model
|字段|含义|
|---|---|
|`id`|数据库主键|
|`name`|报表名称|
|`owner`|报表归属|
|`sql_template`|SQL模版|
|`description`|报表描述|
|`create_at`|创建时间|

# API Contract
POST /reports -> 201 Created
GET /reports -> 200 OK
GET /reports/{id} -> 200 OK / 404 Not Found
PATCH /reports/{id} -> 200 OK / 404 Not Found
DELELE /reports/{id} -> 204 No Content / 404 Not Found
POST /token -> 200 OK / 401 Uauthorized
GET / reports 支持 limit 和 offset 查询参数

# Authentication
 - 1. 先调用 POST /token 获取 access_token
 - 2. 受保护路由需要 Authorization: Bearer <token>
 - 3. 无 token 或者错误 token 返回 401

```bash
curl -X POST http://127.0.0.1:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"

curl http://127.0.0.1:8000/reports \
  -H "Authorization: Bearer catalog-admin-token"
```

# Error Semantics

401 Unauthorized: 未提供 token 或者 token 无效
404 Not Found: 请求的 report 不存在
422 Unprocessable Entity: 请求字段校验失败
201 Created: 成功创建资源
204 No Content: 成功删除资源不返回响应体

# Design Notes

1. 为什么用 dependency injection 提供 DB session
   - 通过 Depends(get_session) 让每个请求获得独立数据库 session, 并在请求结束后通过
   - yield 自动清理，避免在路由中手动管理连接生命力周期。
2. 为什么用 response_model
   - response_model 用于明确响应契约、限制返回字段，并保持 API 文档与实际响应一致。

# Running Locally
```bash
cd projects/02-svc-catalog-rebuild
source .venv/bin/activate
uvicorn app.main:app --relod --port 8000
```
Swagger UI: http://127.0.0.1:8000/docs

# Testing
```bash
source .venv/bin/activate
python -m pytest tests/test_reports.py -q
```

The CI pipeline validates code style with Ruff and runs the reports integration tests with pytest.

当前版本重点覆盖认证 401 和资源不存在 404，403 需要在引入用户身份和授权规则后再补.