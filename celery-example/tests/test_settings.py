from configs.settings import BASE_DIR, LOG_DIR, settings


class TestSettings:
    def test_settings(self):
        assert settings.app_name == "Basic"
        assert settings.app_port == 9527

    def test_global_settings(self):
        assert BASE_DIR.name == "basic"
        assert LOG_DIR.name == "logs"
