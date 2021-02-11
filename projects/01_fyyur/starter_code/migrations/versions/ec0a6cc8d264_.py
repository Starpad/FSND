"""empty message

Revision ID: ec0a6cc8d264
Revises: 4fb11beb9aa6
Create Date: 2020-12-31 17:08:42.069946

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ec0a6cc8d264'
down_revision = '4fb11beb9aa6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('start_time', sa.DateTime(), nullable=False))
    op.drop_column('Show', 'show_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('show_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('Show', 'start_time')
    # ### end Alembic commands ###