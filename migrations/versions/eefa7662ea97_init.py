"""init

Revision ID: eefa7662ea97
Revises:
Create Date: 2023-04-08 14:08:13.913480

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eefa7662ea97"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("login", sa.String(length=64), nullable=False),
        sa.Column("key", sa.String(length=200), nullable=False),
        sa.Column("password", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("key"),
        sa.UniqueConstraint("login"),
    )
    op.create_table(
        "users_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("acc_token", sa.String(length=200), nullable=False),
        sa.Column("exp_time", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], name="fk_users_tokens_users_user_id_user_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("acc_token"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users_tokens")
    op.drop_table("users")
    # ### end Alembic commands ###
