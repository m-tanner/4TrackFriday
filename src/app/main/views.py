import io

from flask import render_template, session, redirect, url_for, current_app, send_file

from src.app import fetcher, db
from src.app.main import main
from src.app.main.forms import NameForm
from src.app.models import User


@main.route("/user_test", methods=["GET", "POST"])
def user_test():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session["known"] = False
            if current_app.config["FLASKY_ADMIN"]:
                # send_email(
                #     current_app.config["FLASKY_ADMIN"],
                #     "New User",
                #     "mail/new_user",
                #     user=user,
                # )
                pass
        else:
            session["known"] = True
        session["name"] = form.name.data
        return redirect(url_for(".user_test"))
    return render_template(
        "user.html",
        form=form,
        name=session.get("name"),
        known=session.get("known", False),
    )


@main.route("/", methods=["GET"])
def index():
    most_recent_episode = fetcher.fetch_most_recent()
    return render_template("episode.html", content=most_recent_episode.content)


@main.route("/spotify", methods=["GET"])
def spotify():
    return render_template(
        "playlist.html",
        content='<iframe src="https://open.spotify.com/embed/playlist/720360kMd4LiSAVzyA8Ft4" '
        'style="width:100%;max-width:660px;overflow:hidden;background:transparent;" '
        'height="450" frameborder="0" allowtransparency="true" allow="encrypted-media">'
        "</iframe>",
    )


@main.route("/apple", methods=["GET"])
def apple():
    return render_template(
        "playlist.html",
        content='<iframe allow="autoplay *; encrypted-media *;" frameborder="0" height="450" '
        'style="width:100%;max-width:660px;overflow:hidden;background:transparent;" '
        'sandbox="allow-forms allow-popups allow-same-origin allow-scripts '
        "allow-storage-access-by-user-activation "
        'allow-top-navigation-by-user-activation" '
        'src="https://embed.music.apple.com/us/playlist/four-track-friday/pl.u-d2b05ZXtLdyjrpg">'
        "</iframe>",
    )


@main.route("/icon", methods=["GET"])
def icon():
    return send_file(
        io.BytesIO(fetcher.fetch_icon("icons/4TF-10.svg")), mimetype="image/svg+xml",
    )


@main.route("/logo", methods=["GET"])
def logo():
    return send_file(
        io.BytesIO(fetcher.fetch_icon("icons/4TF-10.png")), mimetype="image/png",
    )


@main.route("/advert", methods=["GET"])
def advert():
    return send_file(
        io.BytesIO(fetcher.fetch_icon("mVBF8F0.png")), mimetype="image/png",
    )


@main.route("/about", methods=["GET"])
def about():
    return render_template(
        "about.html", content=fetcher.fetch_about(about_key="about.html")
    )


@main.route("/past", methods=["GET"])
def past():
    past_episodes = fetcher.fetch_all()
    return render_template("past.html", past_episodes=past_episodes)


@main.route("/show/<folder>/<content>", methods=["GET"])
def show(folder, content):
    html_string = fetcher.fetch_string_content(f"{folder}/{content}")
    return render_template("episode.html", content=html_string)


@main.route("/health", methods=["GET"])
def health():
    return "", 200
