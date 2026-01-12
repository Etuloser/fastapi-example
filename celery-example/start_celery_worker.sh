#!/bin/bash
# 启动 Celery Worker
celery -A configs.celery_app worker --loglevel=info
