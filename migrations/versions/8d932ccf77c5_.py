"""empty message

Revision ID: 8d932ccf77c5
Revises: b1252997ab47
Create Date: 2020-08-10 22:20:21.031809

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8d932ccf77c5'
down_revision = 'b1252997ab47'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Shows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=True),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('starter_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('Artist', 'past_shows')
    op.drop_column('Artist', 'upcoming_shows')
    op.drop_column('Artist', 'upcoming_shows_count')
    op.drop_column('Artist', 'past_shows_count')
    op.drop_column('Venue', 'past_shows')
    op.drop_column('Venue', 'upcoming_shows')
    op.drop_column('Venue', 'upcoming_shows_count')
    op.drop_column('Venue', 'past_shows_count')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('past_shows_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('Venue', sa.Column('upcoming_shows_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('Venue', sa.Column('upcoming_shows', postgresql.BYTEA(), autoincrement=False, nullable=True))
    op.add_column('Venue', sa.Column('past_shows', postgresql.BYTEA(), autoincrement=False, nullable=True))
    op.add_column('Artist', sa.Column('past_shows_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('Artist', sa.Column('upcoming_shows_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('Artist', sa.Column('upcoming_shows', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('Artist', sa.Column('past_shows', postgresql.BYTEA(), autoincrement=False, nullable=True))
    op.drop_table('Shows')
    # ### end Alembic commands ###