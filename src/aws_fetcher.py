from typing import List

import boto3

from src.cloudfetcher import CloudFetcher
from src.config_manager import ConfigManager
from src.episode import Episode


class AWSCloudFetcher(CloudFetcher):
    def __init__(self, config: ConfigManager):
        self.s3 = boto3.client("s3")
        self.bucket_name = config.static_4tf_bucket

    def fetch_about(self, about_key: str) -> bytes:
        pass

    def fetch_icon(self, icon_key: str) -> bytes:
        return (
            self.s3.get_object(Bucket=self.bucket_name, Key=icon_key).get("Body").read()
        )

    def fetch_string_content(self, episode_key: str) -> str:
        return (
            self.s3.get_object(Bucket=self.bucket_name, Key=episode_key)
            .get("Body")
            .read()
            .decode("utf-8")
        )

    def fetch_most_recent(self) -> Episode:
        episode_objects = self.s3.list_objects(
            Bucket=self.bucket_name, Prefix="episodes"
        ).get("Contents")

        name_of_most_recent = ""
        datetime_of_most_recent = None

        for episode_object in episode_objects[1:]:
            # trim off the first one because it's the folder
            if not datetime_of_most_recent:
                datetime_of_most_recent = episode_object.get("LastModified")
                name_of_most_recent = episode_object.get("Key")
            else:
                datetime_of_last_modification = episode_object.get("LastModified")
                if datetime_of_last_modification > datetime_of_most_recent:
                    datetime_of_most_recent = datetime_of_last_modification
                    name_of_most_recent = episode_object.get("Key")

        response = self.s3.get_object_tagging(
            Bucket=self.bucket_name, Key=name_of_most_recent
        )
        tag_set = response.get("TagSet")

        author, date, episode = "", "", ""

        if len(tag_set) == 3:
            for tag in tag_set:
                if tag.get("Key") == "author":
                    author = tag.get("Value")
                elif tag.get("Key") == "date":
                    date = tag.get("Value")
                elif tag.get("Key") == "episode":
                    episode = tag.get("Value")
            if author and date and episode:
                return Episode(
                    episode=episode,
                    author=author,
                    date=date,
                    cloud_key=name_of_most_recent,
                    content=self.fetch_string_content(episode_key=name_of_most_recent),
                )

        raise ValueError("Couldn't find an episode!")

    def fetch_all(self) -> List[Episode]:
        episode_objects = self.s3.list_objects(
            Bucket=self.bucket_name, Prefix="episodes"
        )

        episode_names = [file.get("Key") for file in episode_objects.get("Contents")]

        past_episodes = []

        for episode_name in episode_names:
            response = self.s3.get_object_tagging(
                Bucket=self.bucket_name, Key=episode_name
            )
            tag_set = response.get("TagSet")

            author, date, episode = "", "", ""

            if len(tag_set) == 3:
                for tag in tag_set:
                    if tag.get("Key") == "author":
                        author = tag.get("Value")
                    elif tag.get("Key") == "date":
                        date = tag.get("Value")
                    elif tag.get("Key") == "episode":
                        episode = tag.get("Value")
                if author and date and episode:
                    this_episode = Episode(
                        episode=episode,
                        author=author,
                        date=date,
                        cloud_key=episode_name,
                        content=self.fetch_string_content(episode_key=episode_name),
                    )
                    past_episodes.append(this_episode)

        past_episodes.sort(key=lambda entry: int(entry.episode), reverse=True)

        return past_episodes
