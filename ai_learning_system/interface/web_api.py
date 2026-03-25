"""
Web API 接口模块

使用 FastAPI 提供 HTTP RESTful API 服务
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from storage.database import Database
from storage.models import Memory


# 全局数据库实例
db: Optional[Database] = None


# Pydantic 模型定义
class MemoryCreate(BaseModel):
    """创建记忆的请求模型"""
    content: str = Field(..., min_length=1, description="记忆内容")
    importance: int = Field(default=5, ge=0, le=10, description="重要性评分 0-10")
    category: str = Field(default="general", description="分类标签")
    privacy_level: int = Field(default=50, ge=0, le=100, description="隐私级别 0-100")
    is_encrypted: bool = Field(default=False, description="是否加密")
    retention_days: int = Field(default=30, ge=0, description="保留天数")


class MemoryResponse(BaseModel):
    """记忆响应模型"""
    id: int
    content: str
    importance: int
    category: str
    created_at: str
    last_accessed: str
    access_count: int
    privacy_level: int
    is_encrypted: bool
    retention_days: int

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    """统计信息响应模型"""
    total_count: int
    category_stats: dict
    avg_importance: float
    avg_privacy_level: float
    encrypted_count: int
    total_access_count: int
    latest_created: Optional[str]


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    在应用启动时初始化数据库连接，关闭时清理资源
    """
    global db
    # 启动事件
    db = Database()
    db.init_tables()
    print("数据库连接已初始化")

    yield

    # 关闭事件
    if db:
        db.close()
        print("数据库连接已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title="AI Learning System API",
    description="AI 学习系统的 Web API 接口",
    version="1.0.0",
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    健康检查接口

    返回服务运行状态
    """
    return {"status": "ok"}


@app.get("/api/memories", response_model=List[MemoryResponse], tags=["Memories"])
async def get_memories(
    limit: int = Query(default=None, ge=1, description="限制返回数量"),
    offset: int = Query(default=0, ge=0, description="偏移量")
):
    """
    获取记忆列表

    支持分页查询
    """
    memories = db.get_all_memories(limit=limit, offset=offset)
    return [memory.to_dict() for memory in memories]


@app.get("/api/memories/{memory_id}", response_model=MemoryResponse, tags=["Memories"])
async def get_memory(memory_id: int):
    """
    获取指定记忆

    根据 ID 获取单个记忆的详细信息
    """
    memory = db.get_memory(memory_id)
    if memory is None:
        raise HTTPException(status_code=404, detail=f"记忆 ID {memory_id} 不存在")
    return memory.to_dict()


@app.post("/api/memories", response_model=MemoryResponse, status_code=201, tags=["Memories"])
async def create_memory(memory_data: MemoryCreate):
    """
    创建新记忆

    创建一个新的记忆条目
    """
    memory_dict = memory_data.model_dump()
    memory = db.create_memory(memory_dict)
    return memory.to_dict()


@app.delete("/api/memories/{memory_id}", tags=["Memories"])
async def delete_memory(memory_id: int):
    """
    删除记忆

    根据 ID 删除指定的记忆
    """
    success = db.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"记忆 ID {memory_id} 不存在")
    return {"message": f"记忆 ID {memory_id} 已成功删除"}


@app.get("/api/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_stats():
    """
    获取统计信息

    返回系统的各种统计数据
    """
    stats = db.get_stats()
    return stats
