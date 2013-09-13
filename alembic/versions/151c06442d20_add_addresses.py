"""add addresses

Revision ID: 151c06442d20
Revises: 198b61210e3e
Create Date: 2013-09-13 14:04:47.069312

"""

# revision identifiers, used by Alembic.
revision = '151c06442d20'
down_revision = '198b61210e3e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("INSERT INTO ip_address(ip, availability, domain_mac) VALUES "
               "('192.168.0.1', 1, '-'),"
               "('192.168.0.2', 1, '-'),"
               "('192.168.0.3', 1, '-'),"
               "('192.168.0.4', 1, '-'),"
               "('192.168.0.5', 1, '-'),"
               "('192.168.0.6', 1, '-'),"
               "('192.168.0.7', 1, '-'),"
               "('192.168.0.8', 1, '-'),"
               "('192.168.0.9', 1, '-'),"
               "('192.168.0.10', 1, '-');")


def downgrade():
    op.execute("DELETE FROM ip_address")
