"""add company_activity and salary_ranes table and relations

Revision ID: 740a44a2bc26
Revises: 39abc949f756
Create Date: 2026-08-23 10:47:59.447804

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '740a44a2bc26'
down_revision: Union[str, Sequence[str], None] = '39abc949f756'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'company_activities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'salary_ranges',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('min_salary', sa.Integer(), nullable=True),
        sa.Column('max_salary', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.add_column('companies', sa.Column('persian_name', sa.String(length=120), nullable=False))
    op.add_column('companies', sa.Column('province_id', sa.Integer(), nullable=False))
    op.add_column('companies', sa.Column('city_id', sa.Integer(), nullable=False))
    op.add_column('companies', sa.Column('activity_id', sa.Integer(), nullable=False))

    # create employee enum type first
    employee_count_enum = sa.Enum(
        '2_10',
        '11_50',
        '51_200',
        '201_500',
        '501_1000',
        '1000_PLUS',
        name='employeecount'
    )

    employee_count_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'companies',
        sa.Column('personnel_count', employee_count_enum, nullable=False)
    )

    op.add_column('companies', sa.Column('logo_path', sa.String(length=500), nullable=True))
    op.add_column('companies', sa.Column('phone_number', sa.String(length=20), nullable=False))

    op.create_foreign_key(None, 'companies', 'company_activities', ['activity_id'], ['id'])
    op.create_foreign_key(None, 'companies', 'cities', ['city_id'], ['id'])
    op.create_foreign_key(None, 'companies', 'provinces', ['province_id'], ['id'])

    op.add_column('job_postings', sa.Column('salary_range_id', sa.Integer(), nullable=False))

    job_posting_status_enum = sa.Enum(
        'active',
        'needs_review',
        'draft',
        'closed',
        'archived',
        name='jobpostingstatus'
    )

    job_posting_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'job_postings',
        sa.Column(
            'status',
            job_posting_status_enum,
            server_default='needs_review',
            nullable=False
        )
    )

    op.create_foreign_key(None, 'job_postings', 'salary_ranges', ['salary_range_id'], ['id'])

    op.drop_column('job_postings', 'minimum_salary')


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        'job_postings',
        sa.Column('minimum_salary', sa.BIGINT(), autoincrement=False, nullable=True)
    )

    op.drop_constraint(None, 'job_postings', type_='foreignkey')
    op.drop_column('job_postings', 'status')
    op.drop_column('job_postings', 'salary_range_id')

    op.drop_constraint(None, 'companies', type_='foreignkey')
    op.drop_constraint(None, 'companies', type_='foreignkey')
    op.drop_constraint(None, 'companies', type_='foreignkey')

    op.drop_column('companies', 'phone_number')
    op.drop_column('companies', 'logo_path')
    op.drop_column('companies', 'personnel_count')
    op.drop_column('companies', 'activity_id')
    op.drop_column('companies', 'city_id')
    op.drop_column('companies', 'province_id')
    op.drop_column('companies', 'persian_name')

    # drop enum types
    sa.Enum(name='employeecount').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='jobpostingstatus').drop(op.get_bind(), checkfirst=True)

    op.drop_table('salary_ranges')
    op.drop_table('company_activities')