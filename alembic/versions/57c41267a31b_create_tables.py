"""create tables

Revision ID: 57c41267a31b
Revises: None
Create Date: 2013-09-13 14:03:31.789780

"""

# revision identifiers, used by Alembic.
revision = '57c41267a31b'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(u'ip_address',
                    sa.Column('ip', sa.String(length=19), nullable=False),
                    sa.Column('availability', sa.Integer(), nullable=True),
                    sa.Column('domain_mac', sa.String(length=300),
                              nullable=True),
                    sa.PrimaryKeyConstraint('ip'))
    op.create_table(u'hosts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=True),
                    sa.PrimaryKeyConstraint('id'))
    op.create_table(u'states',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=200),
                              nullable=True),
                    sa.PrimaryKeyConstraint('id'))
    op.create_table(u'domains',
                    sa.Column('uuid_str', sa.String(length=100),
                              nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=True),
                    sa.Column('memory', sa.String(length=100), nullable=True),
                    sa.Column('host_id', sa.Integer(), nullable=True),
                    sa.Column('state_id', sa.Integer(), nullable=True),
                    sa.Column('mac', sa.String(length=300), nullable=False),
                    sa.ForeignKeyConstraint(['host_id'], ['hosts.id'], ),
                    sa.ForeignKeyConstraint(['state_id'], ['states.id'], ),
                    sa.PrimaryKeyConstraint('uuid_str', 'mac'))
    op.create_table(u'actions',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('time', sa.DateTime(), nullable=True),
                    sa.Column('message', sa.String(length=200), nullable=True),
                    sa.Column('domain_uuid', sa.String(length=100),
                              nullable=True),
                    sa.ForeignKeyConstraint(['domain_uuid'],
                                            ['domains.uuid_str'], ),
                    sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table(u'actions')
    op.drop_table(u'domains')
    op.drop_table(u'states')
    op.drop_table(u'hosts')
    op.drop_table(u'ip_address')