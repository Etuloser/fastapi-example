@echo off
REM 启动 Celery Worker
celery -A configs.celery_app worker -E --loglevel=info --pool=solo
