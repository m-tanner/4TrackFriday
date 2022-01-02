from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL, ValidationError


class PlaylistSubmissionForm(FlaskForm):
    submission = StringField(
        """Click "Share Playlist" on Spotify and submit the link!""",
        validators=[DataRequired(), URL()]
    )
    submit = SubmitField("Submit")

    @staticmethod
    def is_spotify_url(submission: StringField):
        if not submission.data.startswith("https://open.spotify.com/playlist/"):
            raise ValidationError("submission not a valid spotify playlist url")
        return True
