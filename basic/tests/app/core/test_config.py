

from loguru import logger

from app.core.config import BASE_DIR, LOG_DIR, settings


class TestSettings:
    def test_settings(self):
        assert settings.APP_NAME == "Basic"
        assert settings.APP_PORT == 9527
        logger.info(settings.model_dump_json())

    def test_global_settings(self):
        assert BASE_DIR.name == "basic"
        assert LOG_DIR.name == "logs"
