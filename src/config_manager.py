import os


class ConfigManager:
    def __init__(self):
        self.cloud_provider = os.environ["CLOUD_PROVIDER"]  # raises error if not found
        self.gcloud_project = os.environ.get("GCLOUD_PROJECT")
        self.static_4tf_bucket = os.environ.get("STATIC_4TF_BUCKET")
        self.metric_service_url = "https://streaming-service-converter-3-imv2khgjza-uw.a.run.app/v1/statistics"
