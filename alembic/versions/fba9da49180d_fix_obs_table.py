"""fix obs table

Revision ID: fba9da49180d
Revises: efa4e0c0ad7f
Create Date: 2021-05-14 08:47:07.363596

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fba9da49180d'
down_revision = 'efa4e0c0ad7f'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('observation_pk', 'observation', type_='primary')
    op.add_column('observation', sa.Column('id', sa.Integer(), nullable=False,
                                           autoincrement=True, primary_key=True))
    op.create_primary_key("observation_pk", "observation", ['id'])
    op.alter_column('observation', 'value',
                    existing_type=postgresql.DOUBLE_PRECISION(precision=53),
                    nullable=False)
    op.create_unique_constraint(None, 'observation', ['timestamp', 'dataset', 'variable'])


def downgrade():
    op.drop_constraint('observation_timestamp_dataset_variable_key', 'observation', type_='unique')
    op.alter_column('observation', 'value',
                    existing_type=postgresql.DOUBLE_PRECISION(precision=53),
                    nullable=True)
    op.drop_constraint('observation_pk', 'observation', type_='primary')
    op.drop_column('observation', 'id')
    op.create_primary_key("observation_pk", "observation", ['timestamp', 'dataset', 'variable'])
