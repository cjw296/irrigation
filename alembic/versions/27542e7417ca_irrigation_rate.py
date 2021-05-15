"""irrigation rate

Revision ID: 27542e7417ca
Revises: f0ccf576d3fc
Create Date: 2021-05-14 08:39:11.908076

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27542e7417ca'
down_revision = 'f0ccf576d3fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('area', sa.Column('irrigation_rate', sa.Float(), nullable=False))
    op.drop_column('area', 'area')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('area', sa.Column('area', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('area', 'irrigation_rate')
    # ### end Alembic commands ###