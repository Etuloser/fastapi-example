from celery import Celery

from configs.settings import settings

# 创建 Celery 应用实例
celery_app = Celery(
    "celery_example",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# 配置 Celery
celery_app.conf.update(
    # 序列化配置
    task_serializer=settings.celery_task_serializer,
    result_serializer=settings.celery_result_serializer,
    accept_content=settings.celery_accept_content,
    # 时区配置
    timezone=settings.celery_timezone,
    enable_utc=settings.celery_enable_utc,
    # 任务发现
    include=["tasks.example_tasks"],
    # 任务生命周期配置
    result_expires=3600,  # 任务结果过期时间（秒）
    task_time_limit=30 * 60,  # 30 分钟
    task_soft_time_limit=25 * 60,  # 25 分钟
    # Broker 连接配置
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
)
