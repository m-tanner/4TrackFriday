"""add follows

Revision ID: 9120c8a5e20f
Revises: 25d57431da60
Create Date: 2020-05-03 12:44:29.407658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9120c8a5e20f"
down_revision = "25d57431da60"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tracks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("artist", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "likes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("track_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["track_id"], ["tracks.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_likes_timestamp"), "likes", ["timestamp"], unique=False)
    op.create_table(
        "follows",
        sa.Column("follower_id", sa.Integer(), nullable=False),
        sa.Column("followed_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["followed_id"], ["users.id"],),
        sa.ForeignKeyConstraint(["follower_id"], ["users.id"],),
        sa.PrimaryKeyConstraint("follower_id", "followed_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("follows")
    op.drop_index(op.f("ix_likes_timestamp"), table_name="likes")
    op.drop_table("likes")
    op.drop_table("tracks")
    # ### end Alembic commands ###