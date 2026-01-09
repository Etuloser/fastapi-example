from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from configs.logger import logger
from configs.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI 服务启动成功！")
    yield


app = FastAPI(lifespan=lifespan)


class Resp(BaseModel):
    data: dict
    message: str
    code: int = 10020


@app.get("/")
async def root():
    logger.debug("这是一个调试信息")
    logger.info("用户访问了首页")
    logger.warning("这是一个警告信息")
    try:
        1 / 0
    except Exception:
        # 特别强大：一行代码记录完整的错误堆栈
        logger.exception("发生了一个除零错误")
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.app_port,
        log_level="info",
        reload=True,
    )
