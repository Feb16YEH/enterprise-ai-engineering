# 01-svc-hello-rebuild

FastAPI 最小后端服务练习：健康检查、版本信息、Echo接口、同意错误结构、请求日志、middleware。

## Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload

## Docker Run

docker build -t svc-hello .
docker run --rm -p 8000:8000 svc-hello

## APIs

curl http://localhost:8000/health
curl http://localhost:8000/version
curl -X POST http://localhost:8000/echo \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'

## Error Example
curl -X POST http://localhost:8000/echo \
  -H "Content-Type: application/json" \
  -d '{"message":"error"}'

```