"""rename column 'key' to 'name' of settings table

Revision ID: 60b1cfa7d4cc
Revises: 53a60a83b293
Create Date: 2022-09-23 15:28:54.913325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60b1cfa7d4cc'
down_revision = '53a60a83b293'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('name', sa.String(), nullable=True))
    op.drop_column('settings', 'key')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('key', sa.VARCHAR(), nullable=True))
    op.drop_column('settings', 'name')
    # ### end Alembic commands ###
