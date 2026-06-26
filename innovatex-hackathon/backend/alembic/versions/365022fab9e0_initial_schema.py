"""initial_schema

Revision ID: 365022fab9e0
Revises: 
Create Date: 2026-06-26
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '365022fab9e0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 0. Drop legacy tables (from old schema) ─────────────────────────
    op.execute("DROP TABLE IF EXISTS ai_interactions, results, answers, evaluations, company_members, companies, questions, profiles, auth_users CASCADE")

    # ── 1. Blocks ──────────────────────────────────────────────────────
    op.create_table('blocks',
        sa.Column('slug', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('weight', sa.Numeric(5, 2), nullable=False),
        sa.Column('order_num', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('slug'),
        sa.UniqueConstraint('order_num'),
    )

    # ── 2. Profiles ────────────────────────────────────────────────────
    op.create_table('profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['auth.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_profiles_email', 'profiles', ['email'], unique=True)

    # ── 3. Companies ────────────────────────────────────────────────────
    op.create_table('companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('nit', sa.String(20), nullable=False),
        sa.Column('sector', sa.String(100), nullable=True),
        sa.Column('size', sa.String(50), nullable=True),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['profiles.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_companies_nit', 'companies', ['nit'], unique=True)
    op.create_index('ix_companies_created_by', 'companies', ['created_by'])

    # ── 4. Company Members ─────────────────────────────────────────────
    op.create_table('company_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('admin', 'auditor', 'reader', name='role_enum', create_type=False), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'profile_id', name='uq_company_member'),
    )
    op.create_index('ix_company_members_company_id', 'company_members', ['company_id'])
    op.create_index('ix_company_members_profile_id', 'company_members', ['profile_id'])

    # ── 5. Questions ────────────────────────────────────────────────────
    op.create_table('questions',
        sa.Column('slug', sa.String(10), nullable=False),
        sa.Column('block_id', sa.String(50), nullable=False),
        sa.Column('kind', sa.Enum('gate', 'scale', 'validation', name='question_kind_enum', create_type=False), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('weight', sa.Numeric(5, 2), nullable=False),
        sa.Column('order_num', sa.Integer(), nullable=False),
        sa.Column('gate_for', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['block_id'], ['blocks.slug'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('slug'),
        sa.UniqueConstraint('order_num'),
        sa.UniqueConstraint('block_id', 'order_num', name='uq_question_block_order'),
    )
    op.create_index('ix_questions_block_id', 'questions', ['block_id'])

    # ── 6. Assessments ──────────────────────────────────────────────────
    op.create_table('assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('draft', 'completed', name='assessment_status_enum', create_type=False), nullable=False),
        sa.Column('overall_score', sa.Numeric(6, 2), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("status != 'completed' OR overall_score IS NOT NULL", name='ck_completed_has_score'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by'], ['profiles.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_assessments_company_id', 'assessments', ['company_id'])
    op.create_index('ix_assessments_created_by', 'assessments', ['created_by'])

    # ── 7. Assessment Answers (polymorphic) ─────────────────────────────
    op.create_table('assessment_answers',
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', sa.String(10), nullable=False),
        sa.Column('kind', sa.Enum('gate', 'scale', 'validation', name='question_kind_enum', create_type=False), nullable=False),
        sa.Column('scale_resp', sa.SmallInteger(), nullable=True),
        sa.Column('gate_resp', sa.Boolean(), nullable=True),
        sa.Column('validation_resp', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('answered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("scale_resp IS NULL OR scale_resp IN (0, 35, 70, 100)", name='ck_scale_resp_valid'),
        sa.CheckConstraint(
            "(kind = 'gate'        AND gate_resp IS NOT NULL AND scale_resp IS NULL AND validation_resp IS NULL) OR "
            "(kind = 'scale'       AND scale_resp IS NOT NULL AND gate_resp IS NULL AND validation_resp IS NULL) OR "
            "(kind = 'validation'  AND validation_resp IS NOT NULL AND scale_resp IS NULL AND gate_resp IS NULL)",
            name='ck_answer_one_kind'
        ),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.slug'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('assessment_id', 'question_id'),
    )
    op.create_index('ix_assessment_answers_assessment_id', 'assessment_answers', ['assessment_id'])
    op.create_index('ix_assessment_answers_question_id', 'assessment_answers', ['question_id'])

    # ── 8. Scores ───────────────────────────────────────────────────────
    op.create_table('scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('block_id', sa.String(50), nullable=False),
        sa.Column('score', sa.Numeric(6, 2), nullable=False),
        sa.Column('max_score', sa.Numeric(6, 2), nullable=False),
        sa.Column('percentage', sa.Numeric(6, 3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['block_id'], ['blocks.slug'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('assessment_id', 'block_id', name='uq_score_assessment_block'),
    )
    op.create_index('ix_scores_assessment_id', 'scores', ['assessment_id'])
    op.create_index('ix_scores_block_id', 'scores', ['block_id'])

    # ── 9. Recommendations ──────────────────────────────────────────────
    op.create_table('recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('block_id', sa.String(50), nullable=True),
        sa.Column('ai_generated_text', sa.Text(), nullable=False),
        sa.Column('priority', sa.Enum('high', 'medium', 'low', name='priority_enum', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['block_id'], ['blocks.slug'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_recommendations_assessment_id', 'recommendations', ['assessment_id'])

    # ── 10. Action Items ────────────────────────────────────────────────
    op.create_table('action_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', name='action_item_status_enum', create_type=False), nullable=False),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to'], ['profiles.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_action_items_recommendation_id', 'action_items', ['recommendation_id'])
    op.create_index('ix_action_items_assessment_id', 'action_items', ['assessment_id'])
    op.create_index('ix_action_items_assigned_to', 'action_items', ['assigned_to'])

    # ── 11. Share Links ─────────────────────────────────────────────────
    op.create_table('share_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.Enum('active', 'revoked', 'expired', name='share_link_status_enum', create_type=False), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['profiles.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_share_links_token', 'share_links', ['token'], unique=True)
    op.create_index('ix_share_links_assessment_id', 'share_links', ['assessment_id'])


def downgrade() -> None:
    op.drop_table('share_links')
    op.drop_table('action_items')
    op.drop_table('recommendations')
    op.drop_table('scores')
    op.drop_table('assessment_answers')
    op.drop_table('assessments')
    op.drop_table('questions')
    op.drop_table('company_members')
    op.drop_table('companies')
    op.drop_table('profiles')
    op.drop_table('blocks')
    # ENUM types are auto-dropped by SQLAlchemy
