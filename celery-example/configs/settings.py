from pathlib import Path
from urllib.parse import urlencode

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).resolve().parent.parent
LOG_DIR: Path = BASE_DIR / "logs"


class Settings(BaseSettings):
    app_name: str = "celery-example"
    app_port: int = 10862

    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 30379  # Docker 映射的外部端口
    redis_db: int = 0
    redis_password: str = ""  # Redis 密码，如果为空则不使用密码
    redis_username: str = ""  # Redis 用户名（可选，Redis 6.0+）
    redis_use_tls: bool = True  # 是否使用 TLS/SSL 连接（rediss://）
    redis_ssl_cert_reqs: str = (
        "none"  # TLS 证书验证要求：none/optional/required（自签名证书使用 none）
    )
    # Redis TLS 证书文件配置（可选）
    redis_ssl_ca_certs: str = (
        ""  # CA 证书文件路径（用于验证服务器证书，如 redis.crt 或 redis.pem）
    )
    redis_ssl_certfile: str = ""  # 客户端证书文件路径（如果需要客户端证书认证）
    redis_ssl_keyfile: str = ""  # 客户端私钥文件路径（如果需要客户端证书认证）

    # Celery 配置
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    celery_accept_content: list[str] = ["json"]
    celery_timezone: str = "Asia/Shanghai"
    celery_enable_utc: bool = True

    @property
    def celery_broker_url(self) -> str:
        """构建 Celery Broker URL，支持密码验证"""
        return self._build_redis_url()

    @property
    def celery_result_backend(self) -> str:
        """构建 Celery Result Backend URL，支持密码验证"""
        return self._build_redis_url()

    def _build_redis_url_base(self, hide_password: bool = False) -> str:
        """构建 Redis URL 基础部分（协议、认证、主机、端口、数据库）"""
        protocol = "rediss" if self.redis_use_tls else "redis"

        # 构建认证部分
        if self.redis_password:
            password_display = "***" if hide_password else self.redis_password
            if self.redis_username:
                auth_part = f"{self.redis_username}:{password_display}@"
            else:
                auth_part = f":{password_display}@"
        else:
            auth_part = ""

        return f"{protocol}://{auth_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def _resolve_cert_path(self, path: str) -> Path:
        """解析证书文件路径，将相对路径转换为绝对路径"""
        cert_path = Path(path)
        return cert_path.resolve() if not cert_path.is_absolute() else cert_path

    def _add_tls_params(self, url: str) -> str:
        """为 URL 添加 TLS 参数（如果启用 TLS）"""
        if not self.redis_use_tls:
            return url

        # 将字符串值转换为 kombu 期望的常量名称格式
        cert_reqs_map = {
            "none": "CERT_NONE",
            "optional": "CERT_OPTIONAL",
            "required": "CERT_REQUIRED",
        }
        cert_reqs_value = cert_reqs_map.get(
            self.redis_ssl_cert_reqs.lower(), self.redis_ssl_cert_reqs
        )

        # 构建查询参数字典
        params = {"ssl_cert_reqs": cert_reqs_value}

        # 添加证书文件参数（如果提供）
        if self.redis_ssl_ca_certs:
            params["ssl_ca_certs"] = str(
                self._resolve_cert_path(self.redis_ssl_ca_certs)
            )
        if self.redis_ssl_certfile:
            params["ssl_certfile"] = str(
                self._resolve_cert_path(self.redis_ssl_certfile)
            )
        if self.redis_ssl_keyfile:
            params["ssl_keyfile"] = str(self._resolve_cert_path(self.redis_ssl_keyfile))

        # 使用 urllib.parse 构建查询字符串
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}{urlencode(params)}"

    def _build_redis_url(self) -> str:
        """构建 Redis URL，支持密码、用户名和 TLS"""
        base_url = self._build_redis_url_base(hide_password=False)
        return self._add_tls_params(base_url)

    def get_safe_broker_url(self) -> str:
        """获取安全的 Broker URL（隐藏密码），用于日志输出"""
        safe_url = self._build_redis_url_base(hide_password=True)
        return self._add_tls_params(safe_url)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )


settings = Settings()
