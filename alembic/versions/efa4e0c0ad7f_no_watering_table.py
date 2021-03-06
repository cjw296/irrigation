"""no watering table

Revision ID: efa4e0c0ad7f
Revises: 27542e7417ca
Create Date: 2021-05-14 08:40:25.169652

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'efa4e0c0ad7f'
down_revision = '27542e7417ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('watering')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('watering',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('date', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('area_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('source', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('mm', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['area_name'], ['area.name'], name='watering_area_name_fkey'),
    sa.PrimaryKeyConstraint('id', name='watering_pkey')
    )
    # ### end Alembic commands ###
