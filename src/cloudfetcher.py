import abc
from typing import List

from src.episode import Episode


class CloudFetcher(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def fetch_about(self, about_key: str) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_icon(self, icon_key: str) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_string_content(self, episode_key: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_most_recent(self) -> Episode:
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_all(self) -> List[Episode]:
        raise NotImplementedError
