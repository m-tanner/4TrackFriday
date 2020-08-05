from src.app.config.config import Config
from src.app.config.config_types import key_to_type


def get_config(config_type: str) -> Config:
    return key_to_type.get(config_type)
