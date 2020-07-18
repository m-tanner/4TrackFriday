import os


class ConfigManager:
    def __init__(self):
        self.cloud_provider = os.getenv("CLOUD_PROVIDER")
        self.gcloud_project = os.getenv("GCLOUD_PROJECT")
        self.static_4tf_bucket = os.getenv("STATIC_4TF_BUCKET")
