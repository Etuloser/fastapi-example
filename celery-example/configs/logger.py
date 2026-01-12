from loguru import logger

from configs.settings import LOG_DIR

# 确保日志目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)


# 2. 配置 Loguru
def setup_logging():
    # 移除默认的控制台输出（为了自定义格式）
    logger.remove()

    # 添加控制台输出 (带颜色，便于开发调试)
    logger.add(
        sink=lambda msg: print(msg, end=""),
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )

    # 添加文件输出 - 结构化日志（JSON格式）
    logger.add(
        LOG_DIR / "app_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # 每天午夜 0 点创建一个新文件
        retention="30 days",  # 日志保留 30 天
        compression="zip",  # 旧日志自动压缩成 zip
        level="INFO",
        enqueue=True,  # 异步写入，不影响接口性能
        serialize=True,  # 使用loguru内置的JSON序列化
    )


# 初始化
setup_logging()
