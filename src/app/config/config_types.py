from src.app.config.dev_config import DevConfig
from src.app.config.prod_config import ProdConfig
from src.app.config.test_config import TestConfig

key_to_type = {
    "dev": DevConfig,
    "test": TestConfig,
    "stg": ProdConfig,
    "prod": ProdConfig,
    "default": DevConfig,
}
