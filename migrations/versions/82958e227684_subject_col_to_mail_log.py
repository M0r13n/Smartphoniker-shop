"""subject col to mail log

Revision ID: 82958e227684
Revises: 189f923972d0
Create Date: 2020-06-25 17:25:49.922815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82958e227684'
down_revision = '189f923972d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    #op.add_column('mail_log', sa.Column('subject', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###
    pass

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    #op.drop_column('mail_log', 'subject')
    # ### end Alembic commands ###
    pass
