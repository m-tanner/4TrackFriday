import json
from datetime import datetime
from typing import List, Dict

import pytz
from google.cloud import storage

from src.config_manager import ConfigManager
from src.episode import Episode
from src.fetcher import Fetcher


class GCloudFetcher(Fetcher):
    def __init__(self, config: ConfigManager):
        self.client = storage.Client(project=config.gcloud_project)
        self.bucket_name = config.static_4tf_bucket
        self.bucket = self.client.bucket(bucket_name=self.bucket_name)

    def fetch_about(self, about_key: str) -> str:
        return self.fetch_string_content(episode_key=about_key)

    def fetch_icon(self, icon_key: str) -> bytes:
        return self.bucket.get_blob(blob_name=icon_key).download_as_string()

    def fetch_string_content(self, episode_key: str) -> str:
        return (
            self.bucket.get_blob(blob_name=episode_key)
            .download_as_string()
            .decode("utf-8")
        )

    def fetch_most_recent(self) -> Episode:
        blobs = self.client.list_blobs(
            bucket_or_name=self.bucket_name,
            prefix="episodes/",
            delimiter="/",
            fields="items",
        )
        most_recent_blob_updated = pytz.UTC.localize(  # pylint: disable=E1120
            datetime.min
        )
        most_recent_blob = None
        for blob in blobs:
            if blob.updated > most_recent_blob_updated:
                most_recent_blob_updated = blob.updated
                most_recent_blob = blob

        if not most_recent_blob:
            raise RuntimeError("Couldn't fetch any blobs when looking for most recent.")

        episode = most_recent_blob.metadata.get("episode")
        author = most_recent_blob.metadata.get("author")
        date = most_recent_blob.metadata.get("date")
        if not all([episode, author, date]):
            raise RuntimeError("The most recent blob was missing required metadata.")

        return Episode(
            episode=episode,
            author=author,
            date=date,
            cloud_key=most_recent_blob.name,
            content=most_recent_blob.download_as_string().decode("utf-8"),
        )

    def fetch_all(self) -> List[Episode]:
        blobs = self.client.list_blobs(
            bucket_or_name=self.bucket_name,
            prefix="episodes/",
            delimiter="/",
            fields="items",
        )
        episodes: List[Episode] = []
        for blob in blobs:
            if blob.name == "episodes/":
                pass
            else:
                episode = blob.metadata.get("episode")
                author = blob.metadata.get("author")
                date = blob.metadata.get("date")
                if not all([episode, author, date]):
                    raise RuntimeError(
                        "The most recent blob was missing required metadata."
                    )
                episodes.append(
                    Episode(
                        episode=episode,
                        author=author,
                        date=date,
                        cloud_key=blob.name,
                        content=blob.download_as_string().decode("utf-8"),
                    )
                )

        episodes.sort(
            key=lambda entry: [int(s) for s in entry.episode.split(":") if s.isdigit()],
            reverse=True,
        )

        return episodes

    def fetch_metrics(self, path_to_stats: str) -> Dict[str, str]:
        return json.loads(self.fetch_string_content(episode_key=path_to_stats))
