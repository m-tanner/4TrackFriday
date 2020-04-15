from src.aws_fetcher import AWSFetcher
from src.config_manager import ConfigManager
from src.episode import Episode


def test_aws_fetcher():
    episode_fetcher = AWSFetcher(config=ConfigManager())

    episodes = episode_fetcher.fetch_all()
    assert isinstance(episodes, list)
    assert episodes

    most_recent_episode = episode_fetcher.fetch_most_recent()
    assert isinstance(most_recent_episode, Episode)
    assert most_recent_episode
