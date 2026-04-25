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