#!/bin/bash
# 启动 Celery Flower 监控工具
# Celery Flower 会自动从 configs.celery_app 读取 broker URL（包含 SSL 配置）
celery -A configs.celery_app flower --port=5555
