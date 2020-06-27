import io
import os

from flask import Flask, render_template, send_file
from flask_bootstrap import Bootstrap

from src.config_manager import ConfigManager
from src.fetcher_factory import FetcherFactory

import year_in_review
import metrics

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["FTF_SECRET_KEY"]

bootstrap = Bootstrap(app)

config_manager = ConfigManager()
fetcher = FetcherFactory(config=config_manager).get_fetcher()


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


@app.route("/", methods=["GET"])
def index():
    most_recent_episode = fetcher.fetch_most_recent()
    return render_template("episode.html", content=most_recent_episode.content)
    

@app.route("/stats", methods=["GET"])
def stats():
    data = metrics.get_latest_data('metrics')
    return render_template("charts.html", metrics=data)


@app.route("/spotify", methods=["GET"])
def spotify():
    return render_template(
        "playlist.html",
        content='<iframe src="https://open.spotify.com/embed/playlist/720360kMd4LiSAVzyA8Ft4" style="width:100%;max-width:660px;overflow:hidden;background:transparent;" height="450" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>',
    )


@app.route("/apple", methods=["GET"])
def apple():
    return render_template(
        "playlist.html",
        content='<iframe allow="autoplay *; encrypted-media *;" frameborder="0" height="450" style="width:100%;max-width:660px;overflow:hidden;background:transparent;" sandbox="allow-forms allow-popups allow-same-origin allow-scripts allow-storage-access-by-user-activation allow-top-navigation-by-user-activation" src="https://embed.music.apple.com/us/playlist/four-track-friday/pl.u-d2b05ZXtLdyjrpg"></iframe>',
    )


@app.route("/icon", methods=["GET"])
def icon():
    return send_file(
        io.BytesIO(fetcher.fetch_icon("icons/4TF-10.svg")), mimetype="image/svg+xml",
    )


@app.route("/logo", methods=["GET"])
def logo():
    return send_file(
        io.BytesIO(fetcher.fetch_icon("icons/4TF-10.png")), mimetype="image/png",
    )


@app.route("/advert", methods=["GET"])
def advert():
    return send_file(
        io.BytesIO(fetcher.fetch_icon("mVBF8F0.png")), mimetype="image/png",
    )


@app.route("/about", methods=["GET"])
def about():
    return render_template(
        "about.html", content=fetcher.fetch_about(about_key="about.html")
    )


@app.route("/past", methods=["GET"])
def past():
    past_episodes = fetcher.fetch_all()
    return render_template("past.html", past_episodes=past_episodes)


@app.route("/show/<folder>/<content>", methods=["GET"])
def show(folder, content):
    html_string = fetcher.fetch_string_content(f"{folder}/{content}")
    return render_template("episode.html", content=html_string)


@app.route("/health", methods=["GET"])
def health():
    return "", 200


def fetch_playlist_data():
    if config_manager.spotify_auth_token == None:
      config_manager.spotify_auth_token = year_in_review.get_spotify_auth_token()
      print('got a new auth token')
    year_in_review.playlist_info(config_manager.spotify_auth_token)
    metrics.generate_per_feature_metrics()


def run():
    try:
      fetch_playlist_data()
    except Exception as e:
      # swallow Exception
      print(e)
    app.run(host="0.0.0.0", port=80, debug=True)


if __name__ == "__main__":
    run()
