"""add states

Revision ID: 198b61210e3e
Revises: 57c41267a31b
Create Date: 2013-09-13 14:04:13.167189

"""

# revision identifiers, used by Alembic.
revision = '198b61210e3e'
down_revision = '57c41267a31b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("INSERT INTO states(id, name, description) VALUES "
               "(1, 'NOSTATE', 'no state'),"
               "(2, 'RUNNING', 'the domain is running'),"
               "(3, 'BLOCKED', 'the domain is blocked on resource'),"
               "(4, 'PAUSED', 'the domain is paused by user'),"
               "(5, 'SHUTDOWN', 'the domain is being shut down'),"
               "(6, 'SHUTOFF', 'the domain is shut off'),"
               "(7, 'CRASHED', 'the domain is crashed'),"
               "(8, 'PMSUSPENDED', "
               "'the domain is suspended by guest power management'),"
               "(9, 'LAST', 'NB: this enum value will increase over time as "
               "new events are added to the libvirt API. It reflects the last "
               "state supported by this version of the libvirt API.');")


def downgrade():
    op.execute("DELETE FROM states")