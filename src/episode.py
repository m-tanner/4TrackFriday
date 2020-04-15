from dataclasses import dataclass


@dataclass
class Episode:
    episode: str
    author: str
    date: str
    cloud_key: str
    content: str
