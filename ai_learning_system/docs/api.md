# 🌐 Web API 文档

本文档详细介绍 AI 学习系统的 Web API 接口。

## 目录

- [基础信息](#基础信息)
- [接口列表](#接口列表)
- [请求/响应示例](#请求响应示例)
- [错误码说明](#错误码说明)

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API 版本**: v1.0.0
- **Content-Type**: `application/json`
- **API 文档 (Swagger UI)**: `http://localhost:8000/docs`
- **OpenAPI 规范**: `http://localhost:8000/openapi.json`

### 快速开始

```bash
# 启动服务
uvicorn interface.web_api:app --reload

# 测试接口
curl http://localhost:8000/health
```

## 接口列表

### 健康检查

#### GET /health

检查服务运行状态。

**请求参数**: 无

**响应**: `HealthResponse`

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 服务状态，固定为 "ok" |

---

### 记忆管理

#### GET /api/memories

获取记忆列表，支持分页。

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | integer | 否 | 限制返回数量，最小值为 1 |
| offset | integer | 否 | 偏移量，最小值为 0，默认为 0 |

**响应**: `List[MemoryResponse]`

---

#### GET /api/memories/{memory_id}

根据 ID 获取指定记忆的详细信息。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| memory_id | integer | 记忆 ID |

**响应**: `MemoryResponse`

---

#### POST /api/memories

创建新记忆。

**请求体**: `MemoryCreate`

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| content | string | 是 | - | 记忆内容，最小长度 1 |
| importance | integer | 否 | 5 | 重要性评分，范围 0-10 |
| category | string | 否 | "general" | 分类标签 |
| privacy_level | integer | 否 | 50 | 隐私级别，范围 0-100 |
| is_encrypted | boolean | 否 | false | 是否加密 |
| retention_days | integer | 否 | 30 | 保留天数，最小值为 0 |

**响应**: `MemoryResponse` (HTTP 201)

---

#### DELETE /api/memories/{memory_id}

根据 ID 删除指定记忆。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| memory_id | integer | 记忆 ID |

**响应**:

```json
{
  "message": "记忆 ID {memory_id} 已成功删除"
}
```

---

### 统计信息

#### GET /api/stats

获取系统的统计信息。

**请求参数**: 无

**响应**: `StatsResponse`

| 字段 | 类型 | 说明 |
|------|------|------|
| total_count | integer | 总记忆数 |
| category_stats | object | 分类统计，键为分类名，值为数量 |
| avg_importance | float | 平均重要性 |
| avg_privacy_level | float | 平均隐私级别 |
| encrypted_count | integer | 加密记忆数 |
| total_access_count | integer | 总访问次数 |
| latest_created | string | 最近创建时间 (ISO 8601 格式) |

---

## 数据模型

### MemoryCreate

创建记忆的请求模型。

```json
{
  "content": "学习Python编程",
  "importance": 8,
  "category": "learning",
  "privacy_level": 30,
  "is_encrypted": false,
  "retention_days": 365
}
```

### MemoryResponse

记忆响应模型。

```json
{
  "id": 1,
  "content": "学习Python编程",
  "importance": 8,
  "category": "learning",
  "created_at": "2024-01-15T10:30:00",
  "last_accessed": "2024-01-15T10:30:00",
  "access_count": 0,
  "privacy_level": 30,
  "is_encrypted": false,
  "retention_days": 365
}
```

### StatsResponse

统计信息响应模型。

```json
{
  "total_count": 100,
  "category_stats": {
    "general": 50,
    "learning": 30,
    "personal": 20
  },
  "avg_importance": 6.5,
  "avg_privacy_level": 45.0,
  "encrypted_count": 5,
  "total_access_count": 250,
  "latest_created": "2024-01-15T10:30:00"
}
```

---

## 请求/响应示例

### 示例 1: 健康检查

**请求**:

```bash
curl http://localhost:8000/health
```

**响应**:

```json
{
  "status": "ok"
}
```

---

### 示例 2: 创建记忆

**请求**:

```bash
curl -X POST http://localhost:8000/api/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": "今天学习了 FastAPI 框架，感觉非常好用",
    "importance": 8,
    "category": "learning",
    "privacy_level": 20
  }'
```

**响应** (HTTP 201):

```json
{
  "id": 1,
  "content": "今天学习了 FastAPI 框架，感觉非常好用",
  "importance": 8,
  "category": "learning",
  "created_at": "2024-01-15T10:30:00.123456",
  "last_accessed": "2024-01-15T10:30:00.123456",
  "access_count": 0,
  "privacy_level": 20,
  "is_encrypted": false,
  "retention_days": 30
}
```

---

### 示例 3: 获取记忆列表

**请求**:

```bash
curl http://localhost:8000/api/memories?limit=5&offset=0
```

**响应**:

```json
[
  {
    "id": 5,
    "content": "最新的记忆内容",
    "importance": 7,
    "category": "general",
    "created_at": "2024-01-15T12:00:00",
    "last_accessed": "2024-01-15T12:00:00",
    "access_count": 0,
    "privacy_level": 50,
    "is_encrypted": false,
    "retention_days": 30
  },
  {
    "id": 4,
    "content": "另一条记忆",
    "importance": 5,
    "category": "chat",
    "created_at": "2024-01-15T11:00:00",
    "last_accessed": "2024-01-15T11:30:00",
    "access_count": 3,
    "privacy_level": 50,
    "is_encrypted": false,
    "retention_days": 30
  }
]
```

---

### 示例 4: 获取指定记忆

**请求**:

```bash
curl http://localhost:8000/api/memories/1
```

**响应**:

```json
{
  "id": 1,
  "content": "今天学习了 FastAPI 框架，感觉非常好用",
  "importance": 8,
  "category": "learning",
  "created_at": "2024-01-15T10:30:00.123456",
  "last_accessed": "2024-01-15T14:20:00.567890",
  "access_count": 5,
  "privacy_level": 20,
  "is_encrypted": false,
  "retention_days": 30
}
```

**注意**: 获取记忆会自动增加 `access_count` 并更新 `last_accessed`。

---

### 示例 5: 删除记忆

**请求**:

```bash
curl -X DELETE http://localhost:8000/api/memories/1
```

**响应**:

```json
{
  "message": "记忆 ID 1 已成功删除"
}
```

---

### 示例 6: 获取统计信息

**请求**:

```bash
curl http://localhost:8000/api/stats
```

**响应**:

```json
{
  "total_count": 42,
  "category_stats": {
    "general": 20,
    "learning": 15,
    "personal": 5,
    "chat": 2
  },
  "avg_importance": 6.2,
  "avg_privacy_level": 48.5,
  "encrypted_count": 3,
  "total_access_count": 156,
  "latest_created": "2024-01-15T16:45:00.789012"
}
```

---

### 示例 7: 创建加密记忆

**请求**:

```bash
curl -X POST http://localhost:8000/api/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": "我的身份证号是 110101199001011234",
    "importance": 10,
    "category": "personal",
    "privacy_level": 100,
    "is_encrypted": true,
    "retention_days": 3650
  }'
```

**响应** (HTTP 201):

```json
{
  "id": 2,
  "content": "我的身份证号是 110101199001011234",
  "importance": 10,
  "category": "personal",
  "created_at": "2024-01-15T17:00:00.123456",
  "last_accessed": "2024-01-15T17:00:00.123456",
  "access_count": 0,
  "privacy_level": 100,
  "is_encrypted": true,
  "retention_days": 3650
}
```

---

## 错误码说明

### HTTP 状态码

| 状态码 | 说明 | 场景 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 创建成功 |
| 204 | No Content | 删除成功（无返回体） |
| 400 | Bad Request | 请求参数错误 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 请求体验证失败 |
| 500 | Internal Server Error | 服务器内部错误 |

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

### 常见错误示例

#### 404 - 记忆不存在

**请求**:

```bash
curl http://localhost:8000/api/memories/9999
```

**响应** (HTTP 404):

```json
{
  "detail": "记忆 ID 9999 不存在"
}
```

#### 422 - 验证错误

**请求**:

```bash
curl -X POST http://localhost:8000/api/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": "",
    "importance": 15
  }'
```

**响应** (HTTP 422):

```json
{
  "detail": [
    {
      "loc": ["body", "content"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    },
    {
      "loc": ["body", "importance"],
      "msg": "ensure this value is less than or equal to 10",
      "type": "value_error.number.not_le"
    }
  ]
}
```

#### 422 - 类型错误

**请求**:

```bash
curl -X POST http://localhost:8000/api/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": "测试内容",
    "importance": "高"
  }'
```

**响应** (HTTP 422):

```json
{
  "detail": [
    {
      "loc": ["body", "importance"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

---

## 使用 Python 调用 API

```python
import requests

BASE_URL = "http://localhost:8000"

# 健康检查
response = requests.get(f"{BASE_URL}/health")
print(response.json())  # {'status': 'ok'}

# 创建记忆
memory_data = {
    "content": "使用 Python 调用 API",
    "importance": 7,
    "category": "tech"
}
response = requests.post(f"{BASE_URL}/api/memories", json=memory_data)
print(response.json())

# 获取记忆列表
response = requests.get(f"{BASE_URL}/api/memories", params={"limit": 10})
memories = response.json()
for memory in memories:
    print(f"{memory['id']}: {memory['content']}")

# 获取指定记忆
response = requests.get(f"{BASE_URL}/api/memories/1")
print(response.json())

# 删除记忆
response = requests.delete(f"{BASE_URL}/api/memories/1")
print(response.json())

# 获取统计信息
response = requests.get(f"{BASE_URL}/api/stats")
print(response.json())
```

---

## 使用 JavaScript/TypeScript 调用 API

```typescript
const BASE_URL = 'http://localhost:8000';

// 健康检查
fetch(`${BASE_URL}/health`)
  .then(res => res.json())
  .then(data => console.log(data));

// 创建记忆
fetch(`${BASE_URL}/api/memories`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: '使用 JavaScript 调用 API',
    importance: 7,
    category: 'tech'
  }),
})
  .then(res => res.json())
  .then(data => console.log(data));

// 获取记忆列表
fetch(`${BASE_URL}/api/memories?limit=10`)
  .then(res => res.json())
  .then(data => console.log(data));

// 使用 async/await
async function getMemory(id: number) {
  const response = await fetch(`${BASE_URL}/api/memories/${id}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}
```
