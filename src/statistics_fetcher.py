from typing import Any

import requests

from src.config_manager import ConfigManager


class StatisticsFetcher:
    def __init__(self, config: ConfigManager):
        self.metrics_service_url = config.metric_service_url

    def fetch_metrics(self, playlist_id: str) -> Any:
        response = requests.get(
            f"{self.metrics_service_url}/{playlist_id}"
        )
        # TODO add error handling
        return response.json()
