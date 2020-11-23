"""empty message

Revision ID: ddc2ed927aca
Revises: 
Create Date: 2020-11-13 17:41:53.439880

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# required if base_model or ModelMixin is used,
# so that utils.base_model's class can be referenced.
import sys
sys.path.insert(0, "./pt")
import utils

# revision identifiers, used by Alembic.
revision = 'ddc2ed927aca'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('news',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('publish_time', utils.base_models.UTCDatetime(), nullable=False),
    sa.Column('content', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('user',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('account', sa.String(length=80), nullable=False),
    sa.Column('password', sa.String(length=120), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('tag', sa.String(length=120), nullable=False),
    sa.Column('avatar', sa.String(length=120), nullable=True),
    sa.Column('balance', sa.Integer(), nullable=True),
    sa.Column('address', sa.String(length=120), nullable=True),
    sa.Column('eth_address', sa.String(length=80), nullable=True),
    sa.Column('is_aggregator', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('account'),
    sa.UniqueConstraint('tag'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('ami',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('description', sa.String(length=120), nullable=True),
    sa.Column('iota_address', sa.String(length=120), nullable=False),
    sa.Column('time', utils.base_models.UTCDate(), nullable=False),
    sa.Column('time_stamp', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(length=120), nullable=False),
    sa.Column('user_id', postgresql.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.uuid'], ),
    sa.PrimaryKeyConstraint('uuid', 'id'),
    sa.UniqueConstraint('iota_address'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('tag'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('tenders',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('bid_type', sa.String(length=40), nullable=True),
    sa.Column('start_time', utils.base_models.UTCDatetime(), nullable=False),
    sa.Column('end_time', utils.base_models.UTCDatetime(), nullable=False),
    sa.Column('user_id', postgresql.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.uuid'], ),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('bidsubmit',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('bid_type', sa.String(length=40), nullable=True),
    sa.Column('start_time', utils.base_models.UTCDatetime(), nullable=False),
    sa.Column('end_time', utils.base_models.UTCDatetime(), nullable=False),
    sa.Column('value', sa.Float(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('upload_time', utils.base_models.UTCDatetime(), nullable=False),
    sa.Column('tenders_id', postgresql.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['tenders_id'], ['tenders.uuid'], ),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('history',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('description', sa.String(length=120), nullable=True),
    sa.Column('iota_address', sa.String(length=120), nullable=False),
    sa.Column('time', utils.base_models.UTCDate(), nullable=False),
    sa.Column('time_stamp', sa.Integer(), nullable=False),
    sa.Column('ami_id', postgresql.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['ami_id'], ['ami.uuid'], ),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('iota_address'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('matchresult',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('bid_type', sa.String(length=40), nullable=True),
    sa.Column('start_time', utils.base_models.UTCDatetime(), nullable=False),
    sa.Column('end_time', utils.base_models.UTCDatetime(), nullable=False),
    sa.Column('win', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=40), nullable=True),
    sa.Column('counterpart_name', sa.String(length=80), nullable=True),
    sa.Column('counterpart_address', sa.String(length=120), nullable=True),
    sa.Column('bid_value', sa.Float(), nullable=True),
    sa.Column('bid_price', sa.Float(), nullable=True),
    sa.Column('win_value', sa.Float(), nullable=True),
    sa.Column('win_price', sa.Float(), nullable=True),
    sa.Column('achievement', sa.Float(), nullable=True),
    sa.Column('settlement', sa.Float(), nullable=True),
    sa.Column('transaction_hash', sa.String(length=80), nullable=True),
    sa.Column('upload', utils.base_models.UTCDatetime(), nullable=False),
    sa.Column('tenders_id', postgresql.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['tenders_id'], ['tenders.uuid'], ),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('powerdata',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('field', sa.String(length=120), nullable=False),
    sa.Column('updated_at', utils.base_models.UTCDatetime(), nullable=False),
    sa.Column('address', sa.String(length=120), nullable=True),
    sa.Column('history_id', utils.base_models.UUID2STR(as_uuid=True), nullable=False),
    sa.Column('data_type', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['history_id'], ['history.uuid'], ),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('demand',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), nullable=False),
    sa.Column('grid', sa.Float(), nullable=True),
    sa.Column('pv', sa.Float(), nullable=True),
    sa.Column('building', sa.Float(), nullable=True),
    sa.Column('ess', sa.Float(), nullable=True),
    sa.Column('ev', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['uuid'], ['powerdata.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('ess',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), nullable=False),
    sa.Column('cluster', sa.Integer(), nullable=True),
    sa.Column('power_display', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['uuid'], ['powerdata.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('ev',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), nullable=False),
    sa.Column('cluster', sa.Integer(), nullable=True),
    sa.Column('power_display', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['uuid'], ['powerdata.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('pv',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), nullable=False),
    sa.Column('cluster', sa.Integer(), nullable=True),
    sa.Column('pac', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['uuid'], ['powerdata.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('wt',
    sa.Column('uuid', utils.base_models.UUID2STR(as_uuid=True), nullable=False),
    sa.Column('cluster', sa.Integer(), nullable=True),
    sa.Column('windgridpower', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['uuid'], ['powerdata.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wt')
    op.drop_table('pv')
    op.drop_table('ev')
    op.drop_table('ess')
    op.drop_table('demand')
    op.drop_table('powerdata')
    op.drop_table('matchresult')
    op.drop_table('history')
    op.drop_table('bidsubmit')
    op.drop_table('tenders')
    op.drop_table('ami')
    op.drop_table('user')
    op.drop_table('news')
    # ### end Alembic commands ###
