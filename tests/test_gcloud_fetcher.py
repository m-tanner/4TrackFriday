from src.config_manager import ConfigManager
from src.episode import Episode
from src.gcloud_fetcher import GCloudFetcher


def test_aws_fetcher():
    episode_fetcher = GCloudFetcher(config=ConfigManager())

    episodes = episode_fetcher.fetch_all()
    assert isinstance(episodes, list)
    assert episodes

    most_recent_episode = episode_fetcher.fetch_most_recent()
    assert isinstance(most_recent_episode, Episode)
    assert most_recent_episode
