from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from configs.celery_app import celery_app
from configs.logger import logger
from configs.settings import settings
from tasks.example_tasks import add, multiply, send_email_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI 服务启动成功！")
    logger.info("Celery 已集成，broker: {}", settings.get_safe_broker_url())
    yield
    logger.info("FastAPI 服务关闭")


app = FastAPI(lifespan=lifespan, title="Celery Example API")


class Resp(BaseModel):
    data: dict
    message: str


class TaskRequest(BaseModel):
    x: int
    y: int


class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str


@app.get("/")
async def root():
    logger.info("用户访问了首页")
    return {
        "message": "Hello World",
        "description": "FastAPI with Celery integration example",
    }


@app.get("/health")
async def health_check():
    """健康检查，包括 Celery worker 状态"""
    try:
        inspect = celery_app.control.inspect()
        active_workers = inspect.active() or {}

        return {
            "status": "healthy",
            "celery": {
                "broker_url": settings.get_safe_broker_url(),
                "workers": len(active_workers),
                "active_workers": list(active_workers.keys()),
            },
        }
    except Exception as e:
        logger.error("健康检查失败: {}", e)
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "无法连接到 Celery broker 或 worker",
        }


def _create_task_response(task, message: str, **extra_data) -> Resp:
    """创建任务响应的辅助函数"""
    return Resp(
        data={"task_id": task.id, **extra_data},
        message=message,
    )


@app.post("/tasks/add", response_model=Resp)
async def create_add_task(request: TaskRequest):
    """创建加法任务"""
    logger.info("收到加法任务请求: {} + {}", request.x, request.y)
    task = add.delay(request.x, request.y)
    return _create_task_response(task, "加法任务已创建", x=request.x, y=request.y)


@app.post("/tasks/multiply", response_model=Resp)
async def create_multiply_task(request: TaskRequest):
    """创建乘法任务"""
    logger.info("收到乘法任务请求: {} * {}", request.x, request.y)
    task = multiply.delay(request.x, request.y)
    return _create_task_response(task, "乘法任务已创建", x=request.x, y=request.y)


@app.post("/tasks/send-email", response_model=Resp)
async def create_send_email_task(request: EmailRequest):
    """创建发送邮件任务"""
    logger.info("收到发送邮件任务请求: {}", request.to)
    task = send_email_task.delay(request.to, request.subject, request.body)
    return _create_task_response(
        task, "发送邮件任务已创建", to=request.to, subject=request.subject
    )


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    task_result = celery_app.AsyncResult(task_id)
    state = task_result.state
    info = task_result.info or {}

    # 根据任务状态构建响应
    status_map = {
        "PENDING": {
            "status": "任务等待中或不存在",
            "message": "请确保 Celery worker 正在运行"
            if not task_result.ready()
            else None,
        },
        "PROGRESS": {
            "status": "任务执行中",
            "current": info.get("current", 0) if isinstance(info, dict) else 0,
            "total": info.get("total", 1) if isinstance(info, dict) else 1,
        },
        "SUCCESS": {
            "status": "任务执行成功",
            "result": task_result.result,
        },
        "FAILURE": {
            "status": "任务执行失败",
            "error": str(info) if info else "未知错误",
        },
    }

    response = {
        "task_id": task_id,
        "state": state,
        **status_map.get(
            state,
            {
                "status": f"任务状态: {state}",
                "error": str(info) if info else "未知错误",
            },
        ),
    }

    return response


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.app_port,
        log_level="info",
        reload=True,
    )
