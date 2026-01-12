import time

from configs.celery_app import celery_app
from configs.logger import logger


@celery_app.task(name="tasks.add")
def add(x: int, y: int) -> int:
    """简单的加法任务示例"""
    logger.info("执行加法任务: {} + {}", x, y)
    result = x + y
    logger.info("加法任务完成，结果: {}", result)
    return result


@celery_app.task(name="tasks.multiply")
def multiply(x: int, y: int) -> int:
    """简单的乘法任务示例，带延迟模拟耗时操作"""
    logger.info("执行乘法任务: {} * {}", x, y)
    time.sleep(2)  # 模拟耗时操作
    result = x * y
    logger.info("乘法任务完成，结果: {}", result)
    return result


@celery_app.task(name="tasks.send_email_task")
def send_email_task(to: str, subject: str, body: str) -> dict:
    """发送邮件任务示例"""
    logger.info("开始发送邮件到: {}", to)
    logger.info("主题: {}", subject)

    # 模拟发送邮件的过程
    time.sleep(3)

    result = {
        "status": "success",
        "to": to,
        "subject": subject,
        "sent_at": time.time(),
    }
    logger.info("邮件发送成功: {}", result)
    return result
