import io
import os

from flask import Flask, render_template, send_file, redirect, url_for
from flask_bootstrap import Bootstrap

from src.app.main.forms import PlaylistSubmissionForm
from src.config_manager import ConfigManager
from src.fetcher_factory import CloudFetcherFactory
from src.statistics_fetcher import StatisticsFetcher

app = Flask(__name__, root_path=os.path.join(os.getcwd(), "src/app"))
app.config["SECRET_KEY"] = os.environ["FTF_SECRET_KEY"]

bootstrap = Bootstrap(app)

config_manager = ConfigManager()
cloud_fetcher = CloudFetcherFactory(config=config_manager).get_cloud_fetcher()
metrics_fetcher = StatisticsFetcher(config=config_manager)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


@app.route("/", methods=["GET"])
def index():
    most_recent_episode = cloud_fetcher.fetch_most_recent()
    return render_template("episode.html", content=most_recent_episode.content)


@app.route("/stats", methods=["GET"])
def default_stats():
    return redirect(url_for(".stats", playlist_id="720360kMd4LiSAVzyA8Ft4"))


@app.route("/stats/<playlist_id>", methods=["GET"])
def stats(playlist_id: str):
    metrics = metrics_fetcher.fetch_metrics(playlist_id)
    info = metrics.pop("info", None)
    # TODO use the info differently than the rest
    # TODO get the popularity (separate logic required in the scala service)
    return render_template("charts.html", metrics=metrics, info=info)


@app.route("/analyze", methods=["GET", "POST"])
def analyze_from_user():
    # playlist_link is what comes from spotify's "copy link to playlist"
    form = PlaylistSubmissionForm()
    if form.validate_on_submit() and form.is_spotify_url(form.submission):
        submission: str = form.submission.data
        split_submission = submission.split("/")
        playlist_id_with_query_string = split_submission[-1]
        playlist_id = playlist_id_with_query_string.split("?")[0]
        return redirect(url_for(".stats", playlist_id=playlist_id))
    return render_template("analyze.html", form=form)


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


@app.route("/artist_media/<content>", methods=["GET"])
def artist_media(content):
    return send_file(
        io.BytesIO(cloud_fetcher.fetch_icon(f"artist_media/{content}")), mimetype="image/jpg",
    )


@app.route("/icon", methods=["GET"])
def icon():
    return send_file(
        io.BytesIO(cloud_fetcher.fetch_icon("icons/4TF-token.svg")), mimetype="image/svg+xml",
    )


@app.route("/logo", methods=["GET"])
def logo():
    return send_file(
        io.BytesIO(cloud_fetcher.fetch_icon("icons/4TF-10.png")), mimetype="image/png",
    )


@app.route("/advert", methods=["GET"])
def advert():
    return send_file(
        io.BytesIO(cloud_fetcher.fetch_icon("mVBF8F0.png")), mimetype="image/png",
    )


@app.route("/about", methods=["GET"])
def about():
    return render_template(
        "about.html", content=cloud_fetcher.fetch_about(about_key="about.html")
    )


@app.route("/past", methods=["GET"])
def past():
    past_episodes = cloud_fetcher.fetch_all()
    return render_template("past.html", past_episodes=past_episodes)


@app.route("/show/<folder>/<content>", methods=["GET"])
def show(folder, content):
    html_string = cloud_fetcher.fetch_metrics(f"{folder}/{content}")
    return render_template("episode.html", content=html_string)


@app.route("/health", methods=["GET"])
def health():
    return "", 200


def run():
    app.run(host="0.0.0.0", port=80, debug=True)


if __name__ == "__main__":
    run()
