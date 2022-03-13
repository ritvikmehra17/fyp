"""empty message

Revision ID: f29a8ae9c796
Revises: 
Create Date: 2022-03-13 12:10:09.390298

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f29a8ae9c796'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('prediction', sa.Integer(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_data_created_on'), 'message_data', ['created_on'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_created_on'), 'user', ['created_on'], unique=False)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('my_upload',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('img', sa.String(length=255), nullable=True),
    sa.Column('imgtype', sa.String(length=4), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_my_upload_created_at'), 'my_upload', ['created_at'], unique=False)
    op.create_index(op.f('ix_my_upload_updated_at'), 'my_upload', ['updated_at'], unique=False)
    op.create_table('my_cube',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('front', sa.String(length=255), nullable=True),
    sa.Column('back', sa.String(length=255), nullable=True),
    sa.Column('right', sa.String(length=255), nullable=True),
    sa.Column('left', sa.String(length=255), nullable=True),
    sa.Column('ceiling', sa.String(length=255), nullable=True),
    sa.Column('floor', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('publish', sa.Boolean(), nullable=False),
    sa.Column('title', sa.String(length=50), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['back'], ['my_upload.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['ceiling'], ['my_upload.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['floor'], ['my_upload.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['front'], ['my_upload.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['left'], ['my_upload.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['right'], ['my_upload.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_my_cube_created_at'), 'my_cube', ['created_at'], unique=False)
    op.create_table('my_spot',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('cube_id', sa.Integer(), nullable=True),
    sa.Column('x', sa.Integer(), nullable=True),
    sa.Column('y', sa.Integer(), nullable=True),
    sa.Column('z', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cube_id'], ['my_cube.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('my_spot')
    op.drop_index(op.f('ix_my_cube_created_at'), table_name='my_cube')
    op.drop_table('my_cube')
    op.drop_index(op.f('ix_my_upload_updated_at'), table_name='my_upload')
    op.drop_index(op.f('ix_my_upload_created_at'), table_name='my_upload')
    op.drop_table('my_upload')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_created_on'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_message_data_created_on'), table_name='message_data')
    op.drop_table('message_data')
    # ### end Alembic commands ###