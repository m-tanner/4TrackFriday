from src.aws_fetcher import AWSCloudFetcher
from src.config_manager import ConfigManager
from src.gcloud_fetcher import GCloudCloudFetcher


class CloudFetcherFactory:
    def __init__(self, config: ConfigManager):
        self._config = config

    def get_cloud_fetcher(self):
        if self._config.cloud_provider == "AWS":
            return AWSCloudFetcher(config=self._config)
        if self._config.cloud_provider == "gcloud":
            return GCloudCloudFetcher(config=self._config)
        raise RuntimeError(
            "CLOUD_PROVIDER was missing from your environment or "
            "didn't match any known options."
        )
