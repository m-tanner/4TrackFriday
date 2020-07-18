import io

from flask import (
    render_template,
    session,
    redirect,
    url_for,
    current_app,
    send_file,
    flash,
    request,
    make_response,
)
from flask_login import login_required, current_user

from src.app.decorators import admin_required, permission_required
from src.app import fetcher, db
from src.app.sender import send_email
from src.app.main import main
from src.app.main.forms import (
    NameForm,
    EditProfileForm,
    EditProfileAdminForm,
    ContactForm,
)
from src.app.models import User, Role, Permission


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
            if current_app.config["FTF_ADMIN"]:
                send_email(
                    current_app.config["FTF_ADMIN"],
                    "New User",
                    "mail/new_user",
                    user=user,
                )
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


@main.route("/follow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    if current_user.is_following(user):
        flash("You are already following this user.")
        return redirect(url_for(".user", username=username))
    current_user.follow(user)
    db.session.commit()
    flash("You are now following %s." % username)
    return redirect(url_for(".user", username=username))


@main.route("/unfollow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    if not current_user.is_following(user):
        flash("You are not following this user.")
        return redirect(url_for(".user", username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash("You are not following %s anymore." % username)
    return redirect(url_for(".user", username=username))


@main.route("/followers/<username>")
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config["FOLLOWERS_PER_PAGE"], error_out=False
    )
    follows = [
        {"user": item.follower, "timestamp": item.timestamp}
        for item in pagination.items
    ]
    return render_template(
        "followers.html",
        user=user,
        title="Followers of",
        endpoint=".followers",
        pagination=pagination,
        follows=follows,
    )


@main.route("/followed_by/<username>")
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config["FOLLOWERS_PER_PAGE"], error_out=False
    )
    follows = [
        {"user": item.followed, "timestamp": item.timestamp}
        for item in pagination.items
    ]
    return render_template(
        "followers.html",
        user=user,
        title="Followed by",
        endpoint=".followed_by",
        pagination=pagination,
        follows=follows,
    )


@main.route("/all")
@login_required
def show_all():
    resp = make_response(redirect(url_for(".index")))
    resp.set_cookie("show_followed", "", max_age=30 * 24 * 60 * 60)
    return resp


@main.route("/followed")
@login_required
def show_followed():
    resp = make_response(redirect(url_for(".index")))
    resp.set_cookie("show_followed", "1", max_age=30 * 24 * 60 * 60)
    return resp


@main.route("/", methods=["GET"])
def index():
    most_recent_episode = fetcher.fetch_most_recent()
    return render_template("episode.html", content=most_recent_episode.content)


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=user)


@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        current_user.first_artist_forever = form.first_artist_forever.data
        current_user.second_artist_forever = form.second_artist_forever.data
        current_user.favorite_genres = form.favorite_genres.data
        current_user.subscribed = form.subscribed.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash("Your profile has been updated.")
        return redirect(url_for("main.user", username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    form.first_artist_forever.data = current_user.first_artist_forever
    form.second_artist_forever.data = current_user.second_artist_forever
    form.favorite_genres.data = current_user.favorite_genres
    form.subscribed.data = current_user.subscribed
    return render_template("edit_profile.html", form=form)


@main.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data


@main.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        user.first_artist_forever = form.first_artist_forever.data
        user.second_artist_forever = form.second_artist_forever.data
        user.favorite_genres = form.favorite_genres.data
        user.subscribed = form.subscribed.data
        db.session.add(user)
        db.session.commit()
        flash("The profile has been updated.")
        return redirect(url_for("main.user", username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    form.first_artist_forever.data = user.first_artist_forever
    form.second_artist_forever.data = user.second_artist_forever
    form.favorite_genres.data = user.favorite_genres
    form.subscribed.data = user.subscribed
    return render_template("edit_profile.html", form=form, user=user)


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


@main.route("/stats", methods=["GET"])
def stats():
    metrics = fetcher.fetch_metrics("playlist_stats/metrics.json")
    return render_template("charts.html", metrics=metrics)


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


@main.route("/survey/year1", methods=["GET"])
def year_one():
    return render_template(
        "playlist.html",
        content='<script>(function(t,e,s,n){var o,a,c;t.SMCX=t.SMCX||[],e.getElementById(n)||(o=e.getElementsByTagName(s),a=o[o.length-1],c=e.createElement(s),c.type="text/javascript",c.async=!0,c.id=n,c.src="https://widget.surveymonkey.com/collect/website/js/tRaiETqnLgj758hTBazgd_2BNHLyIwmuFE7cezwkskiiyXNdjC0koxkoexplTiSB_2Fg.js",a.parentNode.insertBefore(c,a))})(window,document,"script","smcx-sdk");</script><a style="font: 12px Helvetica, sans-serif; color: #999; text-decoration: none;" href=www.surveymonkey.com> Create your own user feedback survey </a>'
    )


@main.route("/health", methods=["GET"])
def health():
    return "", 200
