from src.config_manager import ConfigManager
from src.statistics_fetcher import StatisticsFetcher


def test_http_fetcher():
    fetcher = StatisticsFetcher(config=ConfigManager())

    json_content = fetcher.fetch_metrics("720360kMd4LiSAVzyA8Ft4")
    assert json_content
    assert """{'tempo': {'name': 'tempo', 'minValue': 49.725, 'minAudioFeature': {'acousticness': 0.673""" \
           in str(json_content)
    assert "null" not in str(json_content)
    # TODO this test is too fragile
